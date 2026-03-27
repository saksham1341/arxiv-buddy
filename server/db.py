from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, TIMESTAMP, Enum, LargeBinary, func, select, URL
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
import enum
from datetime import datetime


class Base(DeclarativeBase):
    pass


class ConversationItemTypes(enum.Enum):
    user_message = "user_message"
    searcher_call = "searcher_call"
    learner_call = "learner_call"
    gather_context_call = "gather_context_call"
    ai_message = "ai_message"
    conversation_state_change = "conversation_state_change"


class ConversationItem(Base):
    __tablename__ = "conversation_items"

    conversation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp(), primary_key=True)
    item_type: Mapped[ConversationItemTypes] = mapped_column(Enum(ConversationItemTypes))
    data: Mapped[bytes] = mapped_column(LargeBinary)

    def to_dict(self) -> dict:
        return {
            "conversation_id": self.conversation_id,
            "timestamp": self.timestamp,
            "item_type": self.item_type.value,
            "data": self.data
        }


class ConversationStateEnum(enum.Enum):
    free = "free"
    busy = "busy"


class ConversationState(Base):
    __tablename__ = "conversation_states"

    conversation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    state: Mapped[ConversationStateEnum] = mapped_column(Enum(ConversationStateEnum))


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

async def get_conversation_state(engine: AsyncEngine, conversation_id: str) -> ConversationStateEnum | None:
    async with AsyncSession(engine) as session:
        res = (await session.execute(select(ConversationState).where(ConversationState.conversation_id == conversation_id).limit(1))).one_or_none()
    
    if res is None:
        return None
    
    return res[0].state

async def set_conversation_state(engine: AsyncEngine, conversation_id: str, state: ConversationStateEnum) -> None:
    async with AsyncSession(engine) as session:
        stmt = insert(ConversationState).values(
            conversation_id=conversation_id,
            state=state
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=[ConversationState.conversation_id],
            set_={
                "state": stmt.excluded.state
            }
        )

        async with session.begin():
            await session.execute(stmt)

async def add_conversation_item(engine: AsyncEngine, conversation_id: str, item_type: ConversationItemTypes, data: bytes, timestamp: datetime | None = None) -> None:
    obj = ConversationItem(
        conversation_id=conversation_id,
        item_type=item_type,
        data=data
    )

    if timestamp:
        obj.timestamp = timestamp

    async with AsyncSession(engine) as session:
        async with session.begin():
            session.add(obj)
