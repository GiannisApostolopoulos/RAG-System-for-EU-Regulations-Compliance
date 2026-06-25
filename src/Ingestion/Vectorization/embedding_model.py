
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL_NAME


class LocalEmbeddingModel:

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model = SentenceTransformer(model_name)


    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple text chunks.
        :param texts: List of text strings to embed
        :return: List of embedding vectors, each as a list of floats
        """
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        return embeddings.tolist()


    def encode_query(self, text: str) -> list[float]:
        """
        Generate an embedding for a single query string.
        :param text: Query text to embed (eg, user question)
        :return: Single embedding vector as a list of floats
        """
        embedding = self.model.encode(
            text,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return embedding.tolist()