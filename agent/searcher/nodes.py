from .state import State
from . import prompts, schemas
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END
import arxiv
from ..llm import light_llm
import asyncio


async def search_query_generator(state: State):
    # For the first invocation, set search_intention to the original query
    # during subsequent invocations search_intention will be preset by the coverage_decider
    search_intention = state.search_intention or state.query

    prompt = prompts.SEARCH_QUERY_GENERATOR_PROMPT
    output_parser = PydanticOutputParser(pydantic_object=schemas.SearchQueryGeneratorOutput)

    chain = prompt | light_llm | output_parser

    resp = await chain.ainvoke(input={
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "QUERY": search_intention
    })

    return {
        "generated_search_queries": resp.queries
    }

# not a node, a helper function
async def search_arxiv(client: arxiv.Client, q: str):
    """
    Search arxiv for a query.

    Args:
        client (arxiv.Client): An instance of arxiv client.
        q (str): The query to search arxiv for.
    
    Returns:
        dict: A dictionary with keys as article ids and values as abstracts.
    """

    search = arxiv.Search(query=q, max_results=10)  # If max_results is not set it lazy loads (potentially infinite) results

    # TODO: implement asynchronous arxiv search
    results = client.results(search)

    return {
        res.get_short_id(): res.summary
        for res in results
    }

async def fetch_articles(state: State, config: RunnableConfig):
    resp = await asyncio.gather(*[search_arxiv(config["configurable"]["arxiv_api_client"], q) for q in state.generated_search_queries])  # type: ignore

    fetched_articles = {}
    for r in resp:
        fetched_articles.update(r)
    
    return {
        "fetched_articles": fetched_articles
    }

async def relevance_filter(state: State):
    if not state.fetched_articles:
        return {
            "relevant_articles": state.relevant_articles
        }
    
    prompt = prompts.RELEVANCE_FILTERING_QUERY
    output_parser = PydanticOutputParser(pydantic_object=schemas.RelevantFilterOutput)

    chain = prompt | light_llm | output_parser

    resp = await chain.ainvoke(input={
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "QUERY": state.search_intention,
        "ARTICLES": state.fetched_articles
    })

    udpated_relevant_articles = state.relevant_articles
    for article_id in resp.relevant_article_ids:
        if article_id not in udpated_relevant_articles:
            udpated_relevant_articles[article_id] = state.fetched_articles[article_id]

    return {
        "relevant_articles": udpated_relevant_articles
    }

async def coverage_decider(state: State):
    prompt = prompts.COVERAGE_DECIDER_QUERY
    output_parser = PydanticOutputParser(pydantic_object=schemas.CoverageDeciderOutput)

    chain = prompt | light_llm | output_parser

    resp = await chain.ainvoke(input={
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "QUERY": state.query,
        "ARTICLES": state.relevant_articles
    })

    if resp.coverage_fulfilled:
        return {
            "search_intention": None
        }
    
    return {
        "search_intention": resp.recommended_search_intention
    }

async def should_continue_searching(state: State):
    if state.search_intention:
        return True
    
    return False
