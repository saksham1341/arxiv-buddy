import arxiv
import asyncio
from kb.client import KBClient
from kb.core.article_part import ArticlePart
from langchain_community.document_loaders import PyMuPDFLoader
from langgraph.graph.state import CompiledStateGraph
from concurrent.futures import ProcessPoolExecutor


async def find_relevant_articles_to_learn(searcher_agent: CompiledStateGraph, arxiv_search_call_semaphore: asyncio.Semaphore, conversation_id: str, q: str) -> list[dict[str, str]]:
    search_results = (await searcher_agent.ainvoke({
        "query": q,  # type: ignore
        "search_attempts": 0,
        "attempts_exhausted": False
    }, config={
        "configurable": {
            "thread_id": conversation_id,
            "arxiv_search_call_semaphore": arxiv_search_call_semaphore  # type: ignore
        },
    }))

    if search_results["attempts_exhausted"]:
        return []

    return search_results["fetched_articles"]

async def learn_article(kb_client: KBClient, learner_agent: CompiledStateGraph, pdf_parser_pool_executor: ProcessPoolExecutor, pdf_parser_pool_executor_semaphore: asyncio.Semaphore, conversation_id: str, article_id: str, pdf_url: str, abstract: str) -> int:
    if await kb_client.is_learned(article_id):
        return 0
    
    apwes = (await learner_agent.ainvoke({
        "article_id": article_id,
        "pdf_url": pdf_url,
        "abstract": abstract
    }, config={
        "configurable": {
            "thread_id": conversation_id,
            "pdf_parser_pool_executor_semaphore": pdf_parser_pool_executor_semaphore,
            "pdf_parser_pool_executor": pdf_parser_pool_executor
        }
    })).get("article_parts_with_embeddable_strings", [])

    await kb_client.add(apwes)

    return len(apwes)

async def generate_context_from_article_parts(aps: list[ArticlePart]) -> str:
    context = "\n".join([ap.content for ap in aps])
    
    return context

async def get_context(kb_client: KBClient, q: list[str], ids: list[str]) -> str:
    aps = await kb_client.query(q, ids)

    full_context = await generate_context_from_article_parts(aps)

    return full_context
