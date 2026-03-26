from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from .config import config


light_llm = ChatGoogleGenerativeAI(
    model=config.light_llm_model
)

heavy_llm = ChatGoogleGenerativeAI(
    model=config.heavy_llm_model
)
