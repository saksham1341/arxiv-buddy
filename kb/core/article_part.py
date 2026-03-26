from pydantic import BaseModel, Field


class ArticlePart(BaseModel):
    id: str = Field(description="The unique article identifier on arxiv.")
    start: int = Field(description="The starting index of the part (inclusive).")
    end: int = Field(description="Then ending index of the part (inclusive).")
