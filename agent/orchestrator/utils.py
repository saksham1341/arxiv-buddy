import arxiv
import asyncio
from kb.client import KBClient
from kb.core.article_part import ArticlePart
from langchain_community.document_loaders import PyMuPDFLoader
from langgraph.graph.state import CompiledStateGraph
from langchain.tools import tool, ToolRuntime


async def find_relevant_articles_to_learn(arxiv_api_client: arxiv.Client, searcher_agent: CompiledStateGraph, conversation_id: str, q: str) -> dict[str, str]:
    relevant_articles = (await searcher_agent.ainvoke({
        "query": q,  # type: ignore
    }, config={
        "configurable": {
            "thread_id": conversation_id,
            "arxiv_api_client": arxiv_api_client  # type: ignore
        },
    }))["fetched_articles"]

    return relevant_articles

async def learn_article(kb_client: KBClient, learner_agent: CompiledStateGraph, conversation_id: str, article_id: str) -> int:
    if await kb_client.is_learned(article_id):
        return 0
    
    apwes = (await learner_agent.ainvoke({
        "article_id": article_id  # type: ignore
    }, config={
        "configurable": {
            "thread_id": conversation_id,
        }
    }))["article_parts_with_embeddable_strings"]

    await kb_client.add(apwes)

    return len(apwes)

async def generate_context_from_article_parts(arxiv_api_client: arxiv.Client, aps: list[ArticlePart]) -> str:
    # TODO: use the client (frontend) to offload api calls to arxiv
    article_ids = [ap.id for ap in aps]
    if not article_ids:
        return ""
    
    search = arxiv.Search(id_list=article_ids)
    results = arxiv_api_client.results(search)

    context = ""
    for idx, res in enumerate(results):
        loader = PyMuPDFLoader(file_path=str(res.pdf_url), mode="single")
        doc = (await loader.aload())[0]
        context += "\n" + doc.page_content[aps[idx].start : aps[idx].end + 1]
    
    return context

async def get_context(kb_client: KBClient, arxiv_api_client: arxiv.Client, q: list[str]) -> str:
    aps_list = await kb_client.query(q)

    full_context = "\n".join(await asyncio.gather(*[generate_context_from_article_parts(arxiv_api_client, aps) for aps in aps_list]))

    return full_context

async def research_and_learn(conversation_id: str, searcher_agent: CompiledStateGraph, learner_agent: CompiledStateGraph, kb_client: KBClient, arxiv_api_client: arxiv.Client, q: str):
    related_articles = await find_relevant_articles_to_learn(arxiv_api_client, searcher_agent, conversation_id, q)
    article_ids = list(related_articles.keys())

    # yield to notify (pretty bad design I know but let's see for now)
    yield article_ids

    # learn articles
    await asyncio.gather(*[learn_article(kb_client, learner_agent, conversation_id, k) for k in article_ids])
