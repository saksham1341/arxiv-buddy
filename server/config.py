from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class ServerConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="server_"
    )

    kb_url: str = Field(description="The url of the kb server.")

    website_url: str = Field(default="http://localhost:5173", description="The website url to add to CORS allow list.")

    database_host: str = Field(default="localhost", description="The host of the database.")
    database_port: int = Field(default=5432, description="The port of the database.")
    database_username: str = Field(description="Username to connect to the database.")
    database_password: str = Field(description="Password to connect to the database.")
    database_name: str = Field(default="arxiv_buddy_kb", description="The name of the database.")

    pdf_parser_pool_executor_semaphore_count: int = Field(default=10, description="Value of the process parser pool semaphore.")
    arxiv_search_call_semaphore_count: int = Field(default=10, description="Value of the arxiv search call semaphore.")


config = ServerConfig()  # type: ignore
