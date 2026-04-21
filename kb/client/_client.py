import httpx
import asyncio
from .config import config
from ..core.article_part import ArticlePart, ArticlePartWithEmbeddableStrings


class KBClient:
    def __init__(self, kb_url: str) -> None:
        self._kb_url = kb_url
    
    async def status(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self._kb_url}/")
            return response.json()

    async def add(self, pwes: list[ArticlePartWithEmbeddableStrings]) -> int:
        batches: list[list[ArticlePartWithEmbeddableStrings]] = []
        start = 0
        while start < len(pwes):
            batches.append(pwes[start: start + config.add_batch_size])
            start += config.add_batch_size
        
        async with httpx.AsyncClient(timeout=60) as client:
            tasks = [client.post(
                url=f"{self._kb_url}/add",
                json={
                    "parts_with_embeddable_strings": [p.model_dump(mode="json") for p in batch]
                }
            ) for batch in batches]

            responses = await asyncio.gather(*tasks)

        return sum([res.json()["count"] if res.status_code == 200 and res.json()["success"] else 0 for res in responses])
    
    async def query(self, q: list[str], ids: list[str]) -> list[ArticlePart]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"{self._kb_url}/query",
                params={
                    "q": q,
                    "ids": ids
                }
            )

            return [ArticlePart.model_validate(part) for part in response.json()["parts"]]
    
    async def is_learned(self, article_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"{self._kb_url}/is_learned",
                params={
                    "article_id": article_id
                }
            )

            return response.json()["is_learned"]
    
    def create_article_part_with_embeddable_strings(self, ap: ArticlePart, es: list[str]) -> ArticlePartWithEmbeddableStrings:
        return ArticlePartWithEmbeddableStrings(
            part=ap,
            embeddable_strings=es
        )
