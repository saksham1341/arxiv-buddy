from pydantic import BaseModel, Field


class ArticleDescriptionOutputSchema(BaseModel):
    description: str = Field(description="A 1-2 line description of the article to prepend to all of it chunks before embedding.")
