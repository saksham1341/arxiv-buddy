from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class KBCoreConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="kb_core_"
    )

    embedding_model: str = Field(default="gemini-embedding-001", description="The model to use for embeddings.")
    embedding_dimensionality: int = Field(default=1536, description="The dimensionality of embeddings.")
    embedding_batch_size: int = Field(default=100, description="The batch size used when calling google embedder.")

config = KBCoreConfig()
