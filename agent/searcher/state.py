from pydantic import BaseModel


class State(BaseModel):
    query: str
    search_intention: str | None = None
    generated_search_queries: list[str] = []
    fetched_articles: list[dict[str, str]] = []
