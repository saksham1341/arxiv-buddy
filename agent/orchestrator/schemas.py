from pydantic import BaseModel, Field


class MessageHistoryCoverageCheckerOutput(BaseModel):
    is_query_complete: bool = Field(description="Whether the user query is self-contained and understandable without prior context.")
    is_query_resolvable_from_history: bool | None = Field(description="If the query is incomplete, whether it can be resolved using the conversation transcript. Null if query is already complete.")
    resolved_query: str | None = Field(description="A fully specified version of the user query reconstructed from message history (only if applicable).")
    is_message_history_enough: bool | None = Field(description="Whether the message history alone is sufficient to answer the query. Null if query is not resolvable.")
    kb_queries: list[str] | None = Field(description="Queries for retrieving missing information from the knowledge base. Null if not needed.")
    response: str | None = Field(description="Final answer if message history is sufficient, OR clarification request if query is not resolvable."    )
    new_conversation_title: str | None = Field(description="New conversation title if previous one was not relevant to the resolved query. Null if no change needed.")
    force_new_research: bool = Field(description="Should we skip KB retreival and do a new research.")
    new_query_to_research: str | None = Field(description="If force_new_research is true, this is the query that will be researched. If not, this is null.")


class KBContextCoverageCheckerOutput(BaseModel):
    is_kb_context_enough: bool = Field(description="Boolean representing wether the context fetched from the knowledge base has enough information to answer the user's query.")
    new_query_to_research: str | None = Field(description="If the knowledge base context is not enough, we research and learn about this singe query, adding more information to the knowlege base. If knowledge base context is enough this can be an empty string or null.")
    response: str | None = Field(description="If the knowledge base context is enough, this is the response to the user's query.")
