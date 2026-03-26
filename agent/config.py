from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AgentConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="agent_"
    )

    light_llm_model: str = Field(default="gemini-2.5-flash", description="The model to use for light LLM.")
    heavy_llm_model: str = Field(default="gemini-2.5-pro", description="The model to use for heavy LLM.")

    learner_splitter_max_text_length: int = Field(default=1000, description="The maximum length of text to send to the semantic splitter LLM.")


config = AgentConfig()
