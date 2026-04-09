from pydantic import BaseModel, Field
from . import schemas
from  datetime import datetime


class FetchedArticle(BaseModel):
    article_id: str
    pdf_url: str
    abstract: str
    authors: list[str]
    publish_date: datetime


class State(BaseModel):
    query: str
    search_attempts: int = 0
    attempts_exhausted: bool = False
    search_intention: str | None = None

    past_generated_search_queries: list[schemas.SearchQueryPlan] = Field(
        default_factory=list
    )

    generated_search_queries: list[schemas.SearchQueryPlan] = Field(
        default_factory=list
    )

    fetched_articles: list[FetchedArticle] = Field(
        default_factory=list
    )
