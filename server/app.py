from fastapi import FastAPI
from fastapi.sse import EventSourceResponse
import arxiv
from kb.client import KBClient
from kb.core.article_part import ArticlePart
from .config import config
from agent.learner import agent as learner_agent
from agent.searcher import agent as searcher_agent
from langchain_community.document_loaders import PyMuPDFLoader
from .db import URL, prepare_database, get_conversation_history, get_conversation_items_after_timestamp
from sqlalchemy.ext.asyncio import create_async_engine
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime


engine = create_async_engine(URL.create(
    drivername="postgresql+psycopg",
    username=config.database_username,
    password=config.database_password,
    host=config.database_host,
    port=config.database_port,
    database=config.database_name
))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # prepare the database
    await prepare_database(engine)

    yield

    # close the engine
    await engine.dispose()

app = FastAPI(
    debug=True,
    lifespan=lifespan
)
kb_client = KBClient(host=config.kb_host, port=config.kb_port)
arxiv_api_client = arxiv.Client(page_size=10)

async def find_relevant_articles_to_learn(q: str) -> dict[str, str]:
    relevant_articles = (await searcher_agent.ainvoke({
        "query": q,  # type: ignore
    }, config={
        "configurable": {
            "thread_id": "server_searcher_test",
            "arxiv_api_client": arxiv_api_client  # type: ignore
        },
    }))["relevant_articles"]

    return relevant_articles

async def learn_article(article_id: str) -> int:
    if await kb_client.is_learned(article_id):
        return 0
    
    apwes = (await learner_agent.ainvoke({
        "article_id": article_id  # type: ignore
    }, config={
        "configurable": {
            "thread_id": "server_learner_test",
        }
    }))["article_parts_with_embeddable_strings"]

    await kb_client.add(apwes)

    return len(apwes)

async def generate_context_from_article_parts(aps: list[ArticlePart]) -> str:
    # TODO: use the client (frontend) to offload api calls to arxiv
    article_ids = [ap.id for ap in aps]
    search = arxiv.Search(id_list=article_ids)
    results = arxiv_api_client.results(search)

    context = ""
    for idx, res in enumerate(results):
        loader = PyMuPDFLoader(file_path=str(res.pdf_url), mode="single")
        doc = (await loader.aload())[0]
        context += "\n" + doc.page_content[aps[idx].start : aps[idx].end + 1]
    
    return context

@app.get("/chat/{conversation_id}", response_class=EventSourceResponse)
async def connect_to_chat(conversation_id: str):
    # first we send the complete coversation history
    history = await get_conversation_history(engine, conversation_id)
    # parse ConversationItems to dictionary
    history = [item.to_dict() for item in history]

    yield history

    # yield new entries
    last_timestamp = history[-1]["timestamp"] if history else datetime.fromtimestamp(0)
    while await asyncio.sleep(0.1, True):
        new_items = await get_conversation_items_after_timestamp(engine, conversation_id, last_timestamp)

        for item in new_items:
            yield item.to_dict()

        last_timestamp = new_items[-1].timestamp if new_items else last_timestamp
