from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class KBCoreConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="kb_client_"
    )

    add_batch_size: int = Field(default=10, description="The maximum ArticlesWithEmbeddableStrings to send in the add request at a time.")


config = KBCoreConfig()
