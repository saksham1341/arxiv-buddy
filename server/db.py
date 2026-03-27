from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Uuid, TIMESTAMP, Enum, LargeBinary, func, select, URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
import enum
from datetime import datetime


class Base(DeclarativeBase):
    pass


class ConversationItemTypes(enum.Enum):
    user_message = enum.auto()
    searcher_call = enum.auto()
    learner_call = enum.auto()
    ai_message = enum.auto()


class ConversationItem(Base):
    __tablename__ = "conversation_items"

    conversation_id: Mapped[str] = mapped_column(Uuid, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp(), primary_key=True)
    item_type: Mapped[str] = mapped_column(Enum(ConversationItemTypes))
    data: Mapped[bytes] = mapped_column(LargeBinary)

    def to_dict(self) -> dict:
        return {
            "conversation_id": self.conversation_id,
            "timestamp": self.timestamp,
            "item_type": self.item_type,
            "data": self.data
        }


async def get_conversation_history(engine: AsyncEngine, conversation_id: str) -> list[ConversationItem]:
    async with AsyncSession(engine) as session:
        res = await session.execute(select(ConversationItem).where(ConversationItem.conversation_id == conversation_id).order_by(ConversationItem.timestamp))
    
    return [i[0] for i in res]

async def get_conversation_items_after_timestamp(engine: AsyncEngine, conversation_id: str, timestamp: datetime) -> list[ConversationItem]:
    async with AsyncSession(engine) as session:
        res = await session.execute(select(ConversationItem).where(ConversationItem.conversation_id == conversation_id).where(ConversationItem.timestamp > timestamp).order_by(ConversationItem.timestamp))
    
    return [i[0] for i in res]

async def prepare_database(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
