from fastapi import FastAPI, Path, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.sse import EventSourceResponse
from kb.client import KBClient
from .config import config
from . import db, schemas, notifications
from sqlalchemy.ext.asyncio import create_async_engine
from contextlib import asynccontextmanager
import asyncio
import json
import uuid
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor

# agents
from agent.learner import build_learner
from agent.searcher import build_searcher
from agent.orchestrator import build_orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    # instantiate required objects
    engine = create_async_engine(db.URL.create(
        drivername="postgresql+psycopg",
        username=config.database_username,
        password=config.database_password,
        host=config.database_host,
        port=config.database_port,
        database=config.database_name
    ))

    kb_client = KBClient(host=config.kb_host, port=config.kb_port)
    pdf_parser_pool_executor = ProcessPoolExecutor()

    searcher = build_searcher(name="searcher_agent")
    learner = build_learner(name="learner_agent")
    orchestrator = build_orchestrator(name="orchestrator_agent", searcher_agent=searcher, learner_agent=learner)

    # prepare the database
    await db.prepare_database(engine)

    # attach
    app.state.engine = engine
    app.state.kb_client = kb_client
    app.state.pdf_parser_pool_executor_semaphore = asyncio.Semaphore(config.pdf_parser_pool_executor_semaphore_count)
    app.state.arxiv_search_call_semaphore = asyncio.Semaphore(config.arxiv_search_call_semaphore_count)
    app.state.pdf_parser_pool_executor = pdf_parser_pool_executor
    app.state.orchestrator = orchestrator

    yield

    # cleanup
    await engine.dispose()
    pdf_parser_pool_executor.shutdown(wait=False)

app = FastAPI(
    debug=True,
    lifespan=lifespan
)

origins = [
    config.website_url,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/chat/{conversation_id}", response_model=schemas.SendMessageResponse)
async def send_message_to_chat(req: schemas.SendMessageRequest, conversation_id: str = Path(...)):
    if conversation_id == "new":
        # new chat, redirect with an available conversation id
        while True:
            # TODO: this is not atomic so can cause problems in rare cases
            conversation_id = str(uuid.uuid4())
            conversation = await db.get_conversation(app.state.engine, conversation_id)
            if conversation is None:
                break
        
        await db.upsert_conversation(app.state.engine, conversation_id, title="New Conversation", state=db.ConversationStates.free)

        return RedirectResponse(
            f"/chat/{conversation_id}"
        )

    conversation = await db.get_conversation(app.state.engine, conversation_id)
    if conversation is None:  # new conversation
        return schemas.SendMessageResponse(
            success=False,
            error="Conversation not found.",
            conversation_id=conversation_id
        )
    elif conversation.state == db.ConversationStates.busy:  # agent already running for this conversation
        return schemas.SendMessageResponse(
            success=False,
            error="Agent is busy right now.",
            conversation_id=conversation_id
        )

    # generate message history
    conv_history = await db.get_conversation_history(app.state.engine, conversation_id)
    message_history_parts = []
    for item in conv_history:
        if item.item_type == db.ConversationItemTypes.user_message:
            data = json.loads(item.data.decode())
            message_history_parts.append(f"==== USER MESSAGE ===\n{data['message']}")
        elif item.item_type == db.ConversationItemTypes.ai_message:
            data = json.loads(item.data.decode())
            message_history_parts.append(f"=== AI MESSAGE ===\n{data['message']}")
    message_history = "\n".join(message_history_parts)

    # agent run
    async def run_agent_as_task():
        try:
            await db.upsert_conversation(app.state.engine, conversation_id, state=db.ConversationStates.busy)
            await app.state.orchestrator.ainvoke({
                "user_message": req.message,
                "message_history": message_history,
                "current_conversation_title": conversation.title
            }, config={  # type: ignore
                "configurable": {
                    "thread_id": conversation_id,
                    "notifications": notifications.generate_notification_functions(app.state.engine),
                    "kb_client": app.state.kb_client,
                    "pdf_parser_pool_executor_semaphore": app.state.pdf_parser_pool_executor_semaphore,
                    "pdf_parser_pool_executor": app.state.pdf_parser_pool_executor,
                    "arxiv_search_call_semaphore": app.state.arxiv_search_call_semaphore
                }
            })
        finally:
            await db.upsert_conversation(app.state.engine, conversation_id, state=db.ConversationStates.free)
    
    asyncio.create_task(run_agent_as_task())

    return schemas.SendMessageResponse(
        success=True,
        conversation_id=conversation_id
    )

@app.get("/chat/{conversation_id}", response_class=EventSourceResponse)
async def connect_to_chat(conversation_id: str = Path(...)):
    # check if conversation exists
    conversation = await db.get_conversation(app.state.engine, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    
    yield {
        "type": "conversation_metadata",
        "data": {
            "title": conversation.title,
            "state": conversation.state.value
        }
    }

    # first we send the complete coversation history
    history = await db.get_conversation_history(app.state.engine, conversation_id)
    # parse ConversationItems to dictionary, skipping metadata changes since we sent the latest one just now
    history = [item.to_dict() for item in history if item.item_type != db.ConversationItemTypes.conversation_metadata_change]

    yield {
        "type": "conversation_history",
        "data": history
    }

    # yield new entries
    last_timestamp = history[-1]["timestamp"] if history else datetime.fromtimestamp(0)
    while await asyncio.sleep(0.1, True):
        new_items = await db.get_conversation_items_after_timestamp(app.state.engine, conversation_id, last_timestamp)

        for item in new_items:
            # metadata changes are a different type of event
            if item.item_type == db.ConversationItemTypes.conversation_metadata_change:
                
                yield {
                    "type": "conversation_metadata",
                    "data": json.loads(item.data)
                }
            else:
                yield {
                    "type": "conversation_message",
                    "data": item.to_dict()
                }

        last_timestamp = new_items[-1].timestamp if new_items else last_timestamp
