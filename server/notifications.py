from sqlalchemy.ext.asyncio import AsyncEngine
from . import db
import json

def generate_notification_functions(engine: AsyncEngine) -> dict:
    async def notify_agent_start(conversation_id: str) -> None:
        await db.upsert_conversation(
            engine=engine,
            conversation_id=conversation_id,
            state=db.ConversationStates.busy
        )

        await db.add_conversation_item(
            engine=engine,
            conversation_id=conversation_id,
            item_type=db.ConversationItemTypes.conversation_metadata_change,
            data=json.dumps({
                "state": db.ConversationStates.busy.value
            }).encode()
        )

    async def notify_agent_finished(conversation_id: str) -> None:
        await db.upsert_conversation(
            engine=engine,
            conversation_id=conversation_id,
            state=db.ConversationStates.free
        )

        await db.add_conversation_item(
            engine=engine,
            conversation_id=conversation_id,
            item_type=db.ConversationItemTypes.conversation_metadata_change,
            data=json.dumps({
                "state": db.ConversationStates.free.value
            }).encode()
        )

    async def notify_user_message(conversation_id: str, message: str) -> None:
        await db.add_conversation_item(
            engine=engine,
            conversation_id=conversation_id,
            item_type=db.ConversationItemTypes.user_message,
            data=json.dumps({
                "message": message
            }).encode()
        )

    async def notify_searcher_call(conversation_id: str, q: list[str]) -> None:
        await db.add_conversation_item(
            engine=engine,
            conversation_id=conversation_id,
            item_type=db.ConversationItemTypes.searcher_call,
            data=json.dumps({
                "q": q
            }).encode()
        )
    
    async def notify_learner_call(conversation_id: str, article_ids: list[str]) -> None:
        await db.add_conversation_item(
            engine=engine,
            conversation_id=conversation_id,
            item_type=db.ConversationItemTypes.learner_call,
            data=json.dumps({
                "article_ids": article_ids
            }).encode()
        )
    
    async def notify_gathering_context_call(conversation_id: str, q: list[str]) -> None:
        await db.add_conversation_item(
            engine=engine,
            conversation_id=conversation_id,
            item_type=db.ConversationItemTypes.gather_context_call,
            data=json.dumps({
                "q": q
            }).encode()
        )
    
    async def notify_ai_message(conversation_id: str, message: str) -> None:
        await db.add_conversation_item(
            engine=engine,
            conversation_id=conversation_id,
            item_type=db.ConversationItemTypes.ai_message,
            data=json.dumps({
                "message": message
            }).encode()
        )

    async def notify_conversation_title_change(conversation_id: str, new_title: str) -> None:
        await db.upsert_conversation(
            engine=engine,
            conversation_id=conversation_id,
            title=new_title
        )

        await db.add_conversation_item(
            engine=engine,
            conversation_id=conversation_id,
            item_type=db.ConversationItemTypes.conversation_metadata_change,
            data=json.dumps({
                "title": new_title
            }).encode()
        )
    
    return {
        "notify_agent_start": notify_agent_start,
        "notify_agent_finished": notify_agent_finished,
        "notify_user_message": notify_user_message,
        "notify_searcher_call": notify_searcher_call,
        "notify_learner_call": notify_learner_call,
        "notify_gathering_context_call": notify_gathering_context_call,
        "notify_ai_message": notify_ai_message,
        "notify_conversation_title_change": notify_conversation_title_change,
    }
