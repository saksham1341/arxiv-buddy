from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from ..core.article_part import ArticlePart, ArticlePartWithEmbeddableStrings
from ..core.embedder import embedder
from .config import config
from .db import (
    prepare_database,
    insert_items,
    get_closest_items,
    create_async_engine,
    get_total_object_count,
    get_article_entry_count,
    URL,
    Item
)
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # prepare the database
    await prepare_database(engine)

    yield

    await engine.dispose(close=True)

# The main app
app = FastAPI(
    debug=True,
    lifespan=lifespan
)
engine = create_async_engine(URL.create(
    drivername="postgresql+psycopg",
    username=config.database_username,
    password=config.database_password,
    host=config.database_host,
    port=config.database_port,
    database=config.database_name
))

class IndexResponse(BaseModel):
    success: bool = Field(description="A boolean representing success.")
    size: int = Field(description="Number of entries in the knowledgebase.")

@app.get("/", response_model=IndexResponse)
async def index():
    return IndexResponse(
        success=True,
        size=await get_total_object_count(engine, Item)
    )


class AddToKnowledgeBaseRequest(BaseModel):
    parts_with_embeddable_strings: list[ArticlePartWithEmbeddableStrings] = Field(description="A list of article parts with embeddable strings to add to the database.")


class AddToKnowledgeBaseResponse(BaseModel):
    success: bool = Field(description="A boolean representing successful addition of article parts to the knowledge base.")
    count: int = Field(description="Number of items added to the knowledge base.")


@app.post("/add", name="Add to knowledge base", response_model=AddToKnowledgeBaseResponse)
async def add(req: AddToKnowledgeBaseRequest):
    item_kwargs = []
    all_embeddable_strings = []
    for pwes in req.parts_with_embeddable_strings:
        for s in pwes.embeddable_strings:
            item_kwargs.append({
                "article_id": pwes.part.id,
                "start_idx": pwes.part.start,
                "end_idx": pwes.part.end
            })

            all_embeddable_strings.append(s)
    
    # TODO: Implement asynchronous embedding by writing a custom helper function
    all_embeddings = embedder.embed_documents(
        texts=all_embeddable_strings,
        batch_size=100
    )

    items = [Item(
        **item_kwargs[i],
        embedding=all_embeddings[i]
    ) for i in range(len(all_embeddable_strings))]

    await insert_items(engine, items)

    return AddToKnowledgeBaseResponse(
        success=True,
        count=len(items)
    )


class QueryKnowledgeBaseResponse(BaseModel):
    parts: list[list[ArticlePart]] = Field(description="A list of article parts matching the requested queries.")


@app.get("/query", name="Query the knowledge base", response_model=QueryKnowledgeBaseResponse)
async def query(q: list[str] = Query()):
    # TODO: Imlement asynchronous embedding
    query_embeddings = embedder.embed_documents(
        texts=q,
        batch_size=100
    )

    db_res = await asyncio.gather(*[get_closest_items(engine, _, config.nearest_items_limit) for _ in query_embeddings])
    
    result = []
    for item_list in db_res:
        article_parts = []
        for item in item_list:
            article_parts.append(ArticlePart(
                id=item.article_id,
                start=item.start_idx,
                end=item.end_idx
            ))
        result.append(article_parts)

    return QueryKnowledgeBaseResponse(
        parts=result
    )


class IsLearnedResponse(BaseModel):
    is_learned: bool = Field(description="A boolean representing if an article is already present in the knowledge base.")

@app.get("/is_learned", name="Is an article in the knowledge base", response_model=IsLearnedResponse)
async def is_learned(article_id: str = Query()):
    entry_count = await get_article_entry_count(engine, article_id)

    return IsLearnedResponse(
        is_learned=(entry_count > 0)
    )
