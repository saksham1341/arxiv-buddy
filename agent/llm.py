from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from .config import config


def light_llm(byok: str):
    return ChatGoogleGenerativeAI(
        model=config.light_llm_model,
        api_key=byok
    )

def heavy_llm(byok: str):
    return ChatGoogleGenerativeAI(
        model=config.heavy_llm_model,
        api_key=byok
    )
