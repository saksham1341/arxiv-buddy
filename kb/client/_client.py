import httpx
import asyncio
from .config import config
from ..core.article_part import ArticlePart, ArticlePartWithEmbeddableStrings


class KBClient:
    def __init__(self, host: str, port: int) -> None:
        self._kb_url = f"http://{host}:{port}"
    
    async def status(self) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self._kb_url}/")
            return response.json()

    async def add(self, pwes: list[ArticlePartWithEmbeddableStrings]) -> int:
        batches = []
        start = 0
        while start < len(pwes):
            batches.append(pwes[start: start + config.add_batch_size])
            start += config.add_batch_size

        async with httpx.AsyncClient(timeout=60) as client:
            tasks = [client.post(
                url=f"{self._kb_url}/add",
                json={
                    "parts_with_embeddable_strings": [p.model_dump() for p in batch]
                }
            ) for batch in batches]

            responses = await asyncio.gather(*tasks)

        return sum([res.json()["count"] if res.status_code == 200 and res.json()["success"] else 0 for res in responses])
    
    async def query(self, q: list[str]) -> list[list[ArticlePart]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"{self._kb_url}/query",
                params={
                    "q": q
                }
            )

            return [[self.create_article_part(**part) for part in part_list] for part_list in response.json()["parts"]]
    
    async def is_learned(self, article_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"{self._kb_url}/is_learned",
                params={
                    "article_id": article_id
                }
            )

            return response.json()["is_learned"]
    
    def create_article_part(self, id: str, start: int, end: int, content: str) -> ArticlePart:
        return ArticlePart(
            id=id,
            start=start,
            end=end,
            content=content
        )
    
    def create_article_part_with_embeddable_strings(self, ap: ArticlePart, es: list[str]) -> ArticlePartWithEmbeddableStrings:
        return ArticlePartWithEmbeddableStrings(
            part=ap,
            embeddable_strings=es
        )
