
import chromadb
from chromadb.config import Settings
from datetime import datetime
from langchain_community.vectorstores.utils import maximal_marginal_relevance as mmr
from src.config import LAMBDA_MULT, FETCH_K, N_RESULTS, VECTOR_DIR, COLLECTION_NAME
import numpy as np


class VectorStore:
    """
    A vector database wrapper for storing and retrieving document chunks with embeddings.
    Provides an interface to a persistent ChromaDB vector store, handling the addition of document chunks with their
    embeddings and performing similarity searches with Maximal Marginal Relevance reranking.
    """

    def __init__(self, persist_path: str = VECTOR_DIR, collection_name: str = COLLECTION_NAME):

        self.client = chromadb.PersistentClient(
            path=persist_path,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            configuration={
                "hnsw": {"space": "cosine"}
            },
        )

    def add_chunks(self, chunks: list[dict], vectors: list[list[float]]) -> None:
        """
        Add or update document chunks and their embeddings in the vector store.

        Args:
            chunks (list[dict]): List of chunk dictionaries, each containing:
                - chunk_id (str): Unique identifier for the chunk
                - page_number (int): Page number the chunk came from
                - URL (str): Source URL of the document
                - title (str): Document title
                - date (str): Document date
                - chunk_content (str): The actual text content of the chunk
            vectors (list[list[float]]): List of embedding vectors corresponding to each chunk.
                Must be in the same order as the chunks list.
        """
        chunk_ids = [chunk["chunk_id"] for chunk in chunks]
        metadata = [
            {
                "source_file": chunk["title"],
                "page_number": chunk["page_number"],
                "source_url": chunk["URL"],
                "source_date": chunk["date"],
            }
            for chunk in chunks
        ]
        documents = [chunk["chunk_content"] for chunk in chunks]

        self.collection.upsert(
            ids=chunk_ids,
            embeddings=vectors,
            metadatas=metadata,
            documents=documents,
        )

        self.collection.modify(
            metadata={"last_updated": str(datetime.now())},
        )

    def search_query(
            self,
            query_vector: list[float],
            n_results: int = N_RESULTS,
            fetch_k: int = FETCH_K
    ) -> list[dict]:
        """
        Search for relevant chunks using a query embedding with MMR reranking.

        Args:
            query_vector (list[float]): The embedding vector of the query.
            n_results (int): The number of final results to return after MMR reranking.
            fetch_k (int, optional): The number of initial candidates to retrieve from
                the vector store before MMR reranking. Defaults to 20. Should be >= n_results.

        Returns:
            list[dict]: A list of dictionaries, each containing:
                - chunk_id (str): Unique identifier of the chunk
                - content (str): The text content of the chunk
                - metadata (dict): Metadata associated with the chunk
                - distance (float): Cosine distance from the query to this chunk
                - embedding (list[float]): The embedding vector of the chunk
        """
        if fetch_k < n_results:
            raise ValueError("Initial candidates (fetch_k) cannot be less than final results (n_results)")

        results = self.collection.query(
            query_embeddings=query_vector,
            n_results=fetch_k,
            include=["embeddings", "documents", "metadatas", "distances"]
        )

        if len(results["ids"]) != 1:
            raise ValueError(f"Expected results for 1 query, got {len(results['ids'])} result batches")

        retrieved = list()

        ids = results["ids"][0]
        embeddings = results["embeddings"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        selected = mmr(
            query_embedding=np.array(query_vector),
            embedding_list=embeddings,
            lambda_mult=LAMBDA_MULT,
            k=n_results,
        )

        embedding_list = embeddings.tolist()

        for i in selected:
            retrieved.append(
                {
                    "chunk_id": ids[i],
                    "content": documents[i],
                    "metadata": metadatas[i],
                    "distance": distances[i],
                    "embedding": embedding_list[i],
                }
            )

        return retrieved