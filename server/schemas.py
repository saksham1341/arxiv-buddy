from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    message: str = Field(description="The message to send.")
    byok: str = Field(description="Your Gemini API Key.")


class SendMessageResponse(BaseModel):
    success: bool = Field(description="Boolean representing success.")
    error: str | None = Field(default=None, description="The error message if sending the message failed.")
    conversation_id: str = Field(description="The conversation ID. Particularly useful field when starting a new covnersation through /chat/new endpoint.")


class ConversationItemInListOfConversations(BaseModel):
    conversation_id: str = Field(description="The conversation ID.")
    title: str = Field(description="The title of the chat.")


class ListOfConversationsResponse(BaseModel):
    conversations: list[ConversationItemInListOfConversations] = Field(description="A list of all chats.")
