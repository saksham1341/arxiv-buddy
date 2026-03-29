from pydantic import BaseModel


class State(BaseModel):
    query: str
    search_intention: str | None = None
    past_generated_search_queries: list[str] = []
    generated_search_queries: list[str] = []
    fetched_articles: list[dict[str, str]] = []
