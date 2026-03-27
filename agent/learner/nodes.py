from langgraph.graph import END
from langchain_community.document_loaders import PyMuPDFLoader
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
        "all_content": all_content
    }

async def semantically_split_content(state: State):
    output_parser = PydanticOutputParser(pydantic_object=schemas.SemanticContentSplitOutputSchema)
    chain = prompts.SEMANTICALLY_SPLIT_CONTENT_PROMPT | light_llm | output_parser

    start = 0
    content_blocks = []
    while start < len(state.all_content):
        content = state.all_content[start: start + config.learner_splitter_max_text_length]
        response = await chain.ainvoke({
            "OUTPUT_INSTRUCTIONS": output_parser.get_format_instructions(),
            "TEXT": content
        })

        new_content_blocks = []
        if len(response.indices) == 0:
            start = len(state.all_content)
        else:
            base = start
            for (s, e) in response.indices:
                new_content_blocks.append((base + s, base + e - 1))
                start = base + e
        
        content_blocks.extend(new_content_blocks)
    
    return {
        "content_blocks": content_blocks
    }

async def generate_embeddable_strings(state: State):
    output_parser = PydanticOutputParser(pydantic_object=schemas.EmbeddableStringsOutputSchema)
    chain = prompts.EMBEDDABLE_STRINGS_GENERATOR_PROMPT | heavy_llm | output_parser

    results = await chain.abatch([{
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "TEXT": state.all_content[t[0]: t[1] + 1]
    } for t in state.content_blocks])

    all_apwes_list = []
    for idx, res in enumerate(results):
        ap = ArticlePart(
            id=state.article_id,
            start=state.content_blocks[idx][0],
            end=state.content_blocks[idx][1]
        )
        apwes = ArticlePartWithEmbeddableStrings(
            part=ap,
            embeddable_strings=res.embeddable_strings
        )

        all_apwes_list.append(apwes)
    
    return {
        "article_parts_with_embeddable_strings": all_apwes_list
    }
