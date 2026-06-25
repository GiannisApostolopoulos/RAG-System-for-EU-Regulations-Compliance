
from src.Ingestion.Vectorization.embedding_model import LocalEmbeddingModel
from src.Ingestion.DB.vector_store import VectorStore
from LLM.llm_factory import LLM
from src.config import TEMPERATURE, LOCAL_AI_MODEL
from LLM.system_prompt import SYSTEM_PROMPT


class Retriever:
    """A RAG (Retrieval-Augmented Generation) system for querying EU regulatory documents."""

    def __init__(self):

        self.vectorizer = LocalEmbeddingModel()
        self.db = VectorStore()
        self.llm = LLM()

    def _retrieve_chunks(self, question: str) -> list[dict]:
        """
        Retrieve relevant document chunks from the vector database.

        Args:
            question (str): The user's question to search for.

        Returns:
            list[dict]: A list of retrieved chunks, each containing:
                - chunk_id (str): Unique identifier for the chunk
                - content (str): The text content of the chunk
                - metadata (dict): Document metadata (source_file, page_number, source_url, source_date)
                - distance (float): Cosine distance from the query
                - embedding (list[float]): The chunk's embedding vector
        """
        query_embedding = self.vectorizer.encode_query(question)
        results = self.db.search_query(query_embedding)
        return results

    def _build_context(self, retrieved_chunks: list[dict]) -> str:
        """
        Build a structured context string from retrieved document chunks.

        Args:
            retrieved_chunks (list[dict]): List of chunks returned by `_retrieve_chunks()`.
            Each chunk should contain 'metadata' and 'content' fields.

        Returns:
            str: A formatted string containing all chunks with their source information (file, page, date, URL) and
            content.
        """
        context_blocks = list()

        for chunk in retrieved_chunks:
            metadata = chunk["metadata"]

            context_blocks.append(
                f"""
                Source file: {metadata.get("source_file", "Unknown source")}
                Page number: {metadata.get("page_number", "Unknown")}
                Date uploaded: {metadata.get("source_date", "Unknown")}
                URL: {metadata.get("source_url", "Unknown URL")}
                Content:
                {chunk["content"]}
                """
            )
        return "\n".join(context_blocks)

    def ask(self, question: str) -> dict:
        """
        Ask a question and get an answer based on retrieved EU regulatory documents.

        This is the main method of the Retriever class. It executes the complete RAG pipeline:
        1. Retrieves relevant document chunks
        2. Builds a context from those chunks
        3. Sends the context and question to the LLM
        4. Returns the generated answer with sources

        Args:
            question (str): The user's question about EU regulations.

        Returns:
            dict: A dictionary containing:
                - question (str): The original question
                - answer (ChatCompletion): The LLM's complete response object
                - retrieved (list[dict]): The retrieved chunks used as context
        """
        results = self._retrieve_chunks(question)
        context = self._build_context(results)

        client = self.llm.get_llm()

        answer = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context: {context}\nQuestion: {question}"}
            ],
            model=LOCAL_AI_MODEL,
            temperature=TEMPERATURE,
        )

        final = {
            "question": question,
            "answer": answer,
            "clean_answer": answer.choices[0].message.content,
            "retrieved": results,
        }

        return final


if __name__ == "__main__":
    # Initialize the retriever
    print("Initializing Retriever...")
    retriever = Retriever()
    print("Ready!\n")

    # Test question
    question = "What is GDPR?"

    print("=" * 60)
    print(f"Question: {question}")
    print("=" * 60)
    print()

    # Get the answer
    result = retriever.ask(question)

    # Print the answer exactly as returned
    print(result['answer'])
    print(result['clean_answer'])
