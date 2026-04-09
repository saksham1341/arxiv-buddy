from pydantic import BaseModel, Field
from datetime import datetime


class ArticlePart(BaseModel):
    id: str = Field(description="The unique article identifier on arxiv.")
    start: int = Field(description="The starting index of the part (inclusive).")
    end: int = Field(description="Then ending index of the part (inclusive).")
    publish_date: datetime = Field(description="The publishing date of the article.")
    authors: list[str] = Field(description="Authors of the article.")
    content: str = Field(description="The content of the article part.")


class ArticlePartWithEmbeddableStrings(BaseModel):
    part: ArticlePart = Field(description="An article part.")
    embeddable_strings: list[str] = Field(description="A list of efficient strings to embed and store in the knowledge base, mapped to the article part.")
