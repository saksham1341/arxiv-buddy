from pydantic import BaseModel
from ...kb.core.article_part import ArticlePartWithEmbeddableStrings


class State(BaseModel):
    article_id: str
    all_content: str = ""
    content_blocks: list[tuple[int, int]] = []
    artile_parts_with_embeddable_strings: list[ArticlePartWithEmbeddableStrings]
