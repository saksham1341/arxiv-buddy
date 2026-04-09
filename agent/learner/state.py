from pydantic import BaseModel, Field
from kb.core.article_part import ArticlePartWithEmbeddableStrings


class State(BaseModel):
    article_id: str
    pdf_url: str
    abstract: str
    all_content: str = ""
    content_blocks: list[tuple[int, int, str]] = Field(default_factory=list)
    article_parts_with_embeddable_strings: list[ArticlePartWithEmbeddableStrings] = Field(default_factory=list)
