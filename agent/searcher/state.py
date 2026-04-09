from pydantic import BaseModel, Field
from . import schemas


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

    fetched_articles: list[dict[str, str]] = Field(
        default_factory=list
    )

    current_search_results_count: int = 0