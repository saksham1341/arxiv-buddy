from langgraph.graph import END
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import PydanticOutputParser
from .state import State
from ..llm import light_llm, heavy_llm
from ..config import config
from . import prompts, schemas
from kb.core.article_part import ArticlePart, ArticlePartWithEmbeddableStrings
import arxiv

async def fetch_article_content(state: State):
    # TODO: Implement asynchronous arxiv search
    client = arxiv.Client(
        page_size=1,
    )
    search = arxiv.Search(id_list=[state.article_id])
    
    result = next(client.results(search=search), None)
    if result is None or result.pdf_url is None:
        raise RuntimeError("Failed to fetch article pdf.")
    
    loader = PyMuPDFLoader(file_path=str(result.pdf_url))
    all_content = ""
    async for doc in loader.alazy_load():
        all_content += doc.page_content
    
    return {
        "abstract": result.summary,
        "all_content": all_content
    }

async def split_content(state: State):
    text_splitter = RecursiveCharacterTextSplitter()

    splits = text_splitter.split_text(state.all_content)

    content_blocks = []
    for s in splits:
        start = state.all_content.index(s)
        end = start + len(s) - 1

        content_blocks.append((start ,end))

    return {
        "content_blocks": content_blocks
    }

async def generate_embeddable_strings(state: State):
    output_parser = PydanticOutputParser(pydantic_object=schemas.ArticleDescriptionOutputSchema)
    chain = prompts.ARTICLE_DESCRIPTION_GENERATOR_PROMPT | light_llm | output_parser

    description = (await chain.ainvoke({
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "ABSTRACT": state.abstract
    })).description

    all_apwes_list = []
    for idx, (start, end) in enumerate(state.content_blocks):
        ap = ArticlePart(
            id=state.article_id,
            start=start,
            end=end
        )
        apwes = ArticlePartWithEmbeddableStrings(
            part=ap,
            embeddable_strings=[description + "\n" + state.all_content[start: end + 1]]
        )

        all_apwes_list.append(apwes)
    
    return {
        "article_parts_with_embeddable_strings": all_apwes_list
    }
