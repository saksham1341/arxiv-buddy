from pydantic import BaseModel, Field


class SearchQueryGeneratorOutput(BaseModel):
    queries: list[str] = Field(description="A list of queries to search Arxiv for as determined by the LLM.")


class RelevantFilterOutput(BaseModel):
    relevant_article_ids: list[str] = Field(description="A list of relevant article ids as determined by the LLM.")


class CoverageDeciderOutput(BaseModel):
    coverage_fulfilled: bool = Field(description="Is the currently available set of articles enough to completely answer the original query?")
    recommended_search_intention: str | None = Field(description="If coverage_fulfilled is false, this should be the single most important thing to search for next. If coverage_fulfilled is true, this can either be an empty string or null.")
