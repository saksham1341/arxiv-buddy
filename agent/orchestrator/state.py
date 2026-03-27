from pydantic import BaseModel


class State(BaseModel):
    message_history: str
    user_message: str
    is_message_history_enough: bool = True
    kb_queries: list[str] = []
    kb_context: str = ""
    is_kb_context_enough: bool = True
    new_query_to_research: str = ""
    ai_response: str = ""
