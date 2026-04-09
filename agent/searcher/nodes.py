from .state import State, FetchedArticle
from . import prompts, schemas
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableConfig
from ..llm import light_llm
from ..config import config
import asyncio
from bs4 import BeautifulSoup
import httpx
from urllib.parse import urlencode
import json
from datetime import datetime
import re


async def search_query_generator(state: State):
    # Check if attempts exhausted
    attempt_count = state.search_attempts + 1
    if attempt_count > config.maximum_search_attempts:
        return {
            "search_attempts": attempt_count,
            "attempts_exhausted": True
        }

    # First invocation uses original query
    search_intention = state.search_intention or state.query

    prompt = prompts.SEARCH_QUERY_GENERATOR_PROMPT
    output_parser = PydanticOutputParser(
        pydantic_object=schemas.SearchQueryGeneratorOutput
    )

    chain = prompt | light_llm | output_parser

    # Serialize previous structured query plans
    past_queries_serialized = json.dumps(
        [
            q.model_dump()
            for q in state.past_generated_search_queries
        ],
        indent=2
    )

    resp = await chain.ainvoke(input={
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "SEARCH_INTENTION": search_intention,
        "PAST_QUERIES": past_queries_serialized
    })

    # IMPORTANT: do NOT update history here
    return {
        "search_attempts": attempt_count,
        "attempts_exhausted": False,
        "generated_search_queries": resp.queries
    }

def extract_results_from_arxiv_page(content: bytes) -> list[FetchedArticle]:
    # use beautifulsoup to extract results
    soup = BeautifulSoup(content, "html.parser")

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
            authors = [_.string for _ in res.find("p", class_="authors").find_all("a") if _.string is not None]  # type: ignore
            publish_date_tag = soup.find(
                "p",
                class_="is-size-7"
            )
            match = re.search(r"Submitted\s+([0-9]{1,2}\s+\w+,\s+\d{4})", publish_date_tag.get_text(" ", strip=True))  # type: ignore
            publish_date = datetime.strptime(match.group(1), "%d %B, %Y")  # type: ignore
        except:
            continue

        articles.append(FetchedArticle(
            article_id=article_id,
            pdf_url=pdf_url,
            abstract=abstract,
            authors=authors,
            publish_date=publish_date
        ))
    
    return articles

# not a node, a helper function
async def search_arxiv(semaphore: asyncio.Semaphore, query_plan: schemas.SearchQueryPlan) -> list[FetchedArticle]:

    async with httpx.AsyncClient() as client:
        base_url = "https://arxiv.org/search/advanced"

        params = {
            "advanced": "1",
            "abstracts": "show",
            "size": 25,
            "order": "-announced_date_first",
            "classification-include_cross_list": "include",
        }

        for i, term in enumerate(query_plan.terms):
            params[f"terms-{i}-operator"] = term.operator
            params[f"terms-{i}-term"] = term.atom
            params[f"terms-{i}-field"] = term.field

        for cls in query_plan.classifications:
            params[f"classification-{cls}"] = "y"

        if query_plan.physics_archive:
            params["classification-physics_archives"] = query_plan.physics_archive

        params["date-filter_by"] = query_plan.date_filter_by

        if query_plan.date_year:
            params["date-year"] = query_plan.date_year

        if query_plan.from_date:
            params["date-from_date"] = query_plan.from_date

        if query_plan.to_date:
            params["date-to_date"] = query_plan.to_date

        url = f"{base_url}?{urlencode(params)}"

        async with semaphore:
            response = await client.get(url, timeout=600)

        if response.status_code != 200:
            return []

    results = extract_results_from_arxiv_page(
        response.content
    )[:config.arxiv_search_article_count]

    return results

async def fetch_articles(state: State, config: RunnableConfig):
    resp = await asyncio.gather(
        *[
            search_arxiv(
                config["configurable"]["arxiv_search_call_semaphore"],  # type: ignore
                q
            )
            for q in state.generated_search_queries
        ],
        return_exceptions=True
    )

    fetched_articles = state.fetched_articles.copy()
    successfully_fetched_queries = []

    for idx, result in enumerate(resp):
        if isinstance(result, BaseException):
            continue

        if result:
            successfully_fetched_queries.append(
                state.generated_search_queries[idx]
            )

            fetched_articles.extend(result)

    # Proper structural dedup while preserving order
    combined_queries = (
        state.past_generated_search_queries
        + successfully_fetched_queries
    )

    seen = set()
    deduped_queries = []

    for query in combined_queries:
        key = json.dumps(query.model_dump(), sort_keys=True)

        if key not in seen:
            seen.add(key)
            deduped_queries.append(query)

    return {
        "fetched_articles": fetched_articles,
        "past_generated_search_queries": deduped_queries
    }

async def coverage_decider(state: State):
    prompt = prompts.COVERAGE_DECIDER_QUERY
    output_parser = PydanticOutputParser(pydantic_object=schemas.CoverageDeciderOutput)

    chain = prompt | light_llm | output_parser

    resp = await chain.ainvoke(input={
        "OUTPUT_FORMAT": output_parser.get_format_instructions(),
        "QUERY": state.query,
        "ARTICLES": ("=" * 50 + "\n").join([article.model_dump_json() for article in state.fetched_articles])
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
