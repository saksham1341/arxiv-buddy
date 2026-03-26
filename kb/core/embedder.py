from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from .config import config

embedder = GoogleGenerativeAIEmbeddings(
    model=config.embedding_model,
    output_dimensionality=config.embedding_dimensionality
)
