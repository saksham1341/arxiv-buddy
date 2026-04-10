from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    select,
    func,
    text,
    Index
)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
)
from sqlalchemy.engine import URL
from pgvector.sqlalchemy import VECTOR
from typing import Type
from datetime import datetime
from ..core.config import config as core_config


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "knowledgebase"

    idx: Mapped[int] = mapped_column(BigInteger(), autoincrement=True, primary_key=True)
    embedding: Mapped[VECTOR] = mapped_column(VECTOR(core_config.embedding_dimensionality))
    article_id: Mapped[str] = mapped_column(String)
    start_idx: Mapped[int] = mapped_column(BigInteger())
    end_idx: Mapped[int] = mapped_column(BigInteger())
    publish_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    authors: Mapped[str] = mapped_column(String())
    content: Mapped[str] = mapped_column(String)

    __table_args__ = (
        Index(
            "ix_knowledgebase_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


async def insert_items(engine: AsyncEngine, items: list[Item]) -> None:
    async with AsyncSession(engine) as session:
        async with session.begin():
            session.add_all(items)

async def get_closest_items(engine: AsyncEngine, q: list[float], ids: list[str], n: int) -> list[tuple[Item, float]]:
    async with AsyncSession(engine) as session:
        distance = Item.embedding.cosine_distance(q)

        stmt = (
            select(Item, distance)
            .order_by(distance)
            .limit(n)
        )

        if ids:
            stmt = stmt.where(Item.article_id.in_(ids))

        res = await session.execute(stmt)

    return [(row[0], row[1]) for row in res]

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
