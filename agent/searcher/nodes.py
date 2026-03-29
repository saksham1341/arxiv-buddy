from .state import State
from . import prompts, schemas
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableConfig
from ..llm import light_llm
from ..config import config
import asyncio
from bs4 import BeautifulSoup
import httpx
from urllib.parse import urlencode


async def search_query_generator(state: State):
    # For the first invocation, set search_intention to the original query
    # during subsequent invocations search_intention will be preset by the coverage_decider
    search_intention = state.search_intention or state.query

    prompt = prompts.SEARCH_QUERY_GENERATOR_PROMPT
    output_parser = PydanticOutputParser(pydantic_object=schemas.SearchQueryGeneratorOutput)

    chain = prompt | light_llm | output_parser

    resp = await chain.ainvoke(input={
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "SEARCH_INTENTION": search_intention,
        "PAST_QUERIES": state.past_generated_search_queries
    })

    return {
        "generated_search_queries": resp.queries
    }

def extract_results_from_arxiv_page(content: bytes) -> list[dict[str, str]]:
    # use beautifulsoup to extract results
    soup = BeautifulSoup(content)

    try:
        results = soup.body.main.find("div", class_="content").ol.find_all("li", class_="arxiv-result")  # type: ignore
    except AttributeError:
        return []
    
    articles = []
    for res in results:
        try:
            article_id = str(res.find("div", class_="is-marginless").find("p", class_="list-title").find("a").string)  # type: ignore
            if article_id.startswith("arXiv:"):
                article_id = article_id[6:]
            pdf_url = str(res.find("div", class_="is-marginless").find("p", class_="list-title").find("span").find(lambda x: x.name == "a" and str(x.string) == "pdf")["href"])  # type: ignore
            abstract = ""
            for tag in res.find("p", class_="abstract").find("span", class_="abstract-full").children:  # type: ignore
                if tag.name == "a":  # type: ignore
                    continue
                elif tag.name is None or (tag.name == "span" and "search-hit" in tag["class"]):  # type: ignore
                    abstract += tag.string  # type: ignore
            
            abstract = abstract.strip()
        except:
            continue

        articles.append({
            "article_id": article_id,
            "pdf_url": pdf_url,
            "abstract": abstract
        })
    
    return articles

# not a node, a helper function
async def search_arxiv(semaphore: asyncio.Semaphore, q: str) -> list[dict[str, str]]:
    """
    Search arxiv for a query.

    Args:
        semaphore (asyncio.Semaphore): A semaphore to control arxiv http call.
        q (str): The query to search arxiv for.
    
    Returns:
        list[dict[str, str]]: A list of objects containing resulting articles.
    """

    async with httpx.AsyncClient() as client:  # type: ignore
        base_url = "https://arxiv.org/search/"
        params = urlencode({
            "query": q,
            "searchtype": "all",
            "source": "header",
            "size": 25,
            "abstracts": "show"
        })

        async with semaphore:
            search_response = await client.get(f"{base_url}?{params}", timeout = 600)  # type: ignore

        if search_response.status_code != 200:
            return []
        
    results = extract_results_from_arxiv_page(search_response.content)[:config.arxiv_search_article_count]
    
    return results

async def fetch_articles(state: State, config: RunnableConfig):
    resp = await asyncio.gather(*[search_arxiv(config["configurable"]["arxiv_search_call_semaphore"], q) for q in state.generated_search_queries], return_exceptions=True)  # type: ignore

    fetched_articles = state.fetched_articles.copy()
    successfully_fetched_queries = []
    for idx, r in enumerate(resp):
        if not isinstance(r, BaseException) and r:
            successfully_fetched_queries.append(state.generated_search_queries[idx])
        fetched_articles.extend(r)  # type: ignore
    
    return {
        "fetched_articles": fetched_articles,
        "past_generated_search_queries": list(set(state.past_generated_search_queries + successfully_fetched_queries))
    }

async def coverage_decider(state: State):
    prompt = prompts.COVERAGE_DECIDER_QUERY
    output_parser = PydanticOutputParser(pydantic_object=schemas.CoverageDeciderOutput)

    chain = prompt | light_llm | output_parser

    resp = await chain.ainvoke(input={
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "QUERY": state.query,
        "ARTICLES": {article["article_id"]: article["abstract"] for article in state.fetched_articles}
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
