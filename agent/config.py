from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AgentConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="agent_"
    )

    light_llm_model: str = Field(default="gemini-2.5-flash", description="The model to use for light LLM.")
    heavy_llm_model: str = Field(default="gemini-2.5-flash", description="The model to use for heavy LLM.")

    arxiv_search_article_count: int = Field(default=3, description="Maximum nunber of top articles to take from an arxiv search.")
    maximum_search_attempts: int = Field(default=2, description="Maximum number of loops allowed for searcher agent.")


config = AgentConfig()
