from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, TIMESTAMP, Enum, LargeBinary, func, select, URL, ForeignKey
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
import enum
from datetime import datetime


class Base(DeclarativeBase):
    pass


class ConversationStates(enum.Enum):
    free = "free"
    busy = "busy"


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, default="")
    state: Mapped[ConversationStates] = mapped_column(Enum(ConversationStates))


class ConversationItemTypes(enum.Enum):
    user_message = "user_message"
    searcher_call = "searcher_call"
    learner_call = "learner_call"
    gather_context_call = "gather_context_call"
    ai_message = "ai_message"
    conversation_metadata_change = "conversation_metadata_change"


class ConversationItem(Base):
    __tablename__ = "conversation_items"

    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.conversation_id", ondelete="CASCADE"), primary_key=True)
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

async def get_conversation(engine: AsyncEngine, conversation_id: str) -> Conversation | None:
    async with AsyncSession(engine) as session:
        res = (await session.execute(select(Conversation).where(Conversation.conversation_id == conversation_id).limit(1))).one_or_none()
    
    if res is None:
        return None
    
    return res[0]

async def upsert_conversation(engine: AsyncEngine, conversation_id: str, title: str | None = None, state: ConversationStates | None = None) -> None:
    conversation = await get_conversation(engine, conversation_id)
    updates = {}
    if conversation is not None:
        updates = {
            "title": conversation.title,
            "state": conversation.state
        }
    
    if title is not None:
        updates["title"] = title
    if state is not None:
        updates["state"] = state
    
    async with AsyncSession(engine) as session:
        stmt = insert(Conversation).values(
            conversation_id=conversation_id,
            **updates
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=[Conversation.conversation_id],
            set_={
                "title": stmt.excluded.title,
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

async def get_all_conversations(engine: AsyncEngine) -> list[Conversation]:
    async with AsyncSession(engine) as session:
        all_conversations = await session.execute(select(Conversation))
    
    return [res[0] for res in all_conversations]
