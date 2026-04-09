from langgraph.graph import END
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableConfig
from .state import State
from ..llm import light_llm, heavy_llm
from ..config import config
from . import prompts, schemas
from kb.core.article_part import ArticlePart, ArticlePartWithEmbeddableStrings
import asyncio
import re


def fetch_article_content_helper(url: str) -> str:
    """
    Target of multiprocessing which uses CPU heavy PyMuPDFLoader to read a pdf at given url.
    """

    try:
        loader = PyMuPDFLoader(file_path=str(url), mode="single")
        all_content = loader.load()[0].page_content
    except BaseException:
        all_content = ""
    
    return all_content

async def fetch_article_content(state: State, config: RunnableConfig):
    # use pdf_parser_pool_executor to run a separate process to fetch the content of the pdf
    semaphore = config["configurable"]["pdf_parser_pool_executor_semaphore"]  # type: ignore
    pool_executor = config["configurable"]["pdf_parser_pool_executor"]  # type: ignore
    loop = asyncio.get_event_loop()
    async with semaphore:
        # skip fetching (it will continue in bg though) after 60 seconds.
        try:
            async with asyncio.timeout(60):
                all_content = await loop.run_in_executor(pool_executor, fetch_article_content_helper, state.pdf_url)
        except asyncio.TimeoutError:
            all_content = ""
        
        # clean
        all_content = re.sub(r'[\x00-\x1F\x7F]', '', all_content)
        all_content = all_content.strip()

    return {
        "abstract": state.abstract,
        "all_content": all_content
    }

async def split_content(state: State):
    text_splitter = RecursiveCharacterTextSplitter()

    splits = text_splitter.split_text(state.all_content)

    content_blocks = []
    for s in splits:
        start = state.all_content.index(s)
        end = start + len(s) - 1

        content_blocks.append((start, end, s))

    return {
        "content_blocks": content_blocks
    }

async def generate_embeddable_strings(state: State):
    output_parser = PydanticOutputParser(pydantic_object=schemas.ArticleDescriptionOutputSchema)
    chain = prompts.ARTICLE_DESCRIPTION_GENERATOR_PROMPT | light_llm | output_parser

    # description = (await chain.ainvoke({
    #     "OUTPUT_FORMAT": output_parser.get_format_instructions(),
    #     "ABSTRACT": state.abstract
    # })).description
    description = ""

    all_apwes_list = []
    for (start, end, content) in state.content_blocks:
        ap = ArticlePart(
            id=state.article_id,
            start=start,
            end=end,
            content=content
        )
        apwes = ArticlePartWithEmbeddableStrings(
            part=ap,
            embeddable_strings=[description + "\n" + content]
        )

        all_apwes_list.append(apwes)
    
    return {
        "article_parts_with_embeddable_strings": all_apwes_list
    }
