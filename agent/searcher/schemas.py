from pydantic import BaseModel, Field
from typing import Literal, Optional


class ArxivSearchAtom(BaseModel):
    operator: Literal["AND", "OR", "NOT"] = Field(
        description=(
            "Boolean operator connecting this atomic term to the previous row "
            "in arXiv Advanced Search."
        )
    )

    atom: str = Field(
        description=(
            "Exactly ONE atomic search phrase, acronym, keyword, author name, "
            "or TeX expression. Never include grouped boolean expressions, "
            "parentheses, or multiple concepts in one atom."
        )
    )

    field: Literal[
        "title",
        "author",
        "abstract",
        "comments",
        "journal_ref",
        "acm_class",
        "msc_class",
        "report_num",
        "paper_id",
        "cross_list_category",
        "doi",
        "orcid",
        "author_id",
        "all",
    ] = Field(
        description=(
            "Field to target in arXiv advanced search for this atom."
        )
    )


class SearchQueryPlan(BaseModel):
    terms: list[ArxivSearchAtom] = Field(
        description=(
            "Ordered list of atomic search rows for arXiv advanced search. "
            "Each row must contain exactly one atomic concept."
        )
    )

    classifications: list[
        Literal[
            "computer_science",
            "economics",
            "eess",
            "mathematics",
            "physics",
            "q_biology",
            "q_finance",
            "statistics",
        ]
    ] = Field(default_factory=list)

    physics_archive: Optional[str] = Field(
        default=None,
        description="Optional physics subarchive such as astro-ph or quant-ph."
    )

    date_filter_by: Literal[
        "all_dates",
        "past_12",
        "specific_year",
        "date_range"
    ] = "all_dates"

    date_year: Optional[str] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None


class SearchQueryGeneratorOutput(BaseModel):
    queries: list[SearchQueryPlan]


class RelevantFilterOutput(BaseModel):
    relevant_article_ids: list[str] = Field(
        description="A list of relevant article ids as determined by the LLM."
    )


class CoverageDeciderOutput(BaseModel):
    coverage_fulfilled: bool = Field(
        description=(
            "Is the currently available set of articles enough to completely "
            "answer the original query?"
        )
    )

    recommended_search_intention: str | None = Field(
        description=(
            "If coverage_fulfilled is false, this should be the single most "
            "important thing to search for next. "
            "If coverage_fulfilled is true, this should be null."
        )
    )
