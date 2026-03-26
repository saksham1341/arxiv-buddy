from pydantic import BaseModel, Field


class SemanticContentSplitOutputSchema(BaseModel):
    indices: list[tuple[int, int]] = Field(default=[], description="List of pairs of starting and ending indices to split the content at.")


class EmbeddableStringsOutputSchema(BaseModel):
    embeddable_strings: list[str] = Field(default=[], description="List of high-quality, retrieval-optimized embedding strings for a content block.")
