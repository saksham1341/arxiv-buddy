from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class ServerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="server_"
    )

    kb_host: str = Field(description="The host address of the kb server.")
    kb_port: int = Field(description="The port of the kb server.")

    database_host: str = Field(default="localhost", description="The host of the database.")
    database_port: int = Field(default=5432, description="The port of the database.")
    database_username: str = Field(description="Username to connect to the database.")
    database_password: str = Field(description="Password to connect to the database.")
    database_name: str = Field(default="arxiv_buddy_kb", description="The name of the database.")


config = ServerConfig()  # type: ignore
