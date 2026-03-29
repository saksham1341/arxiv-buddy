from pydantic import BaseModel, Field


class MessageHistoryCoverageCheckerOutput(BaseModel):
    is_message_history_enough: bool = Field(description="Boolean representing wether the given message history has enough context to answer the user's query.")
    kb_queries: list[str] | None = Field(description="If the message history is not enough, we query the knowledge base for these queries and gather context. If message history is enough this can be an empty list or null.")
    response: str | None = Field(description="If the message history is enough, this is the response to the user's query.")

class KBContextCoverageCheckerOutput(BaseModel):
    is_kb_context_enough: bool = Field(description="Boolean representing wether the context fetched from the knowledge base has enough information to answer the user's query.")
    new_query_to_research: str | None = Field(description="If the knowledge base context is not enough, we research and learn about this singe query, adding more information to the knowlege base. If knowledge base context is enough this can be an empty string or null.")
    response: str | None = Field(description="If the knowledge base context is enough, this is the response to the user's query.")
