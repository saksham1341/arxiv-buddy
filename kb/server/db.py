from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy import (
    BigInteger,
    String,
    select,
    func,
    text
)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)
from sqlalchemy.engine import URL
from pgvector.sqlalchemy import VECTOR
from typing import Type
from ..core.config import config as core_config


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "knowledgebase"

    idx: Mapped[int] = mapped_column(BigInteger(), autoincrement=True, primary_key=True)
    embedding: Mapped[VECTOR] = mapped_column(VECTOR(core_config.embedding_dimensionality))
    article_id: Mapped[str] = mapped_column(String(100))
    start_idx: Mapped[int] = mapped_column(BigInteger())
    end_idx: Mapped[int] = mapped_column(BigInteger())


async def insert_items(engine: AsyncEngine, items: list[Item]) -> None:
    async with AsyncSession(engine) as session:
        async with session.begin():
            session.add_all(items)

async def get_closest_items(engine: AsyncEngine, q: list[float], n: int) -> list[Item]:
    async with AsyncSession(engine) as session:
        res = await session.execute(select(Item).order_by(Item.embedding.l2_distance(q)).limit(n))
    
    return [i[0] for i in res] # type: ignore

async def get_total_object_count(engine: AsyncEngine, obj: Type[Base]) -> int:
    async with AsyncSession(engine) as session:
        res = await session.scalar(
            select(func.count()).select_from(obj)
        ) or 0
    
    return res

async def prepare_database(engine: AsyncEngine):
    async with AsyncSession(engine) as session:
        await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await session.commit()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_article_entry_count(engine: AsyncEngine, article_id: str) -> int:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(func.count())
            .select_from(Item)
            .where(Item.article_id == article_id)
        )
        count = result.scalar() or 0

    return count
