from pydantic import BaseModel


class State(BaseModel):
    message_history: str
    user_message: str
    is_query_complete: bool = True
    is_query_resolvable_from_history: bool | None = None
    resolved_query: str | None = None
    user_intent: str | None = None
    is_message_history_enough: bool | None = None
    kb_queries: list[str] | None = None
    kb_context: str | None = None
    is_kb_context_enough: bool = True
    new_query_to_research: str | None = None
    ai_response: str | None = None