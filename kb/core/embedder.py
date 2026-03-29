from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_google_genai._common import GoogleGenerativeAIError
from .config import config
import asyncio

_embedder = GoogleGenerativeAIEmbeddings(
    model=config.embedding_model,
    output_dimensionality=config.embedding_dimensionality
)

async def embedder(texts: list[str]) -> list[list[float]]:
    while True:
        try:
            resp = await asyncio.to_thread(_embedder.embed_documents, texts=texts, output_dimensionality=config.embedding_dimensionality, batch_size=config.embedding_batch_size)
        except GoogleGenerativeAIError:
            await asyncio.sleep(5)
        else:
            break
    
    return resp
