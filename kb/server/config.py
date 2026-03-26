from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class KBServerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="kb_server_"
    )

    database_host: str = Field(default="localhost", description="The host of the database.")
    database_port: int = Field(default=5432, description="The port of the database.")
    database_username: str = Field(description="Username to connect to the database.")
    database_password: str = Field(description="Password to connect to the database.")
    database_name: str = Field(default="arxiv_buddy_kb", description="The name of the database.")

    nearest_items_limit: int = Field(default=10, description="The maximum number of nearest items to the query to return.")


config = KBServerConfig()  # type: ignore
