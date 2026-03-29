from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    message: str = Field(description="The message to send.")


class SendMessageResponse(BaseModel):
    success: bool = Field(description="Boolean representing success.")
    error: str | None = Field(default=None, description="The error message if sending the message failed.")
    conversation_id: str = Field(description="The conversation ID. Particularly useful field when starting a new covnersation through /chat/new endpoint.")
