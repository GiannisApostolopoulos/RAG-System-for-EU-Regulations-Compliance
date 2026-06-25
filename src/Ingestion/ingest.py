
from splitters.pdf_splitter import PdfSplitter
from Vectorization.embedding_model import LocalEmbeddingModel
from downloader import Downloader
from DB.vector_store import VectorStore
from src.config import (DOCS_DIR,
                        VECTOR_DIR,
                        LANGUAGE,
                        FILE_TYPE,
                        CELEX_LIST,
                        )
import os

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)


def run_ingestion():

    # ========== DOWNLOAD DOCUMENTS =============

    downloader = Downloader(FILE_TYPE, DOCS_DIR, LANGUAGE)

    for idx, celex_id in enumerate(CELEX_LIST.values()):
        try:
            downloader.download(celex_id)
        except Exception as e:
            print(e)
            continue

    # ========== SPLIT DOCUMENTS =============

    splitter = PdfSplitter()

    all_chunks = list()

    for file in os.listdir(DOCS_DIR):
        full_path = str(os.path.join(DOCS_DIR, file))
        file_chunks = splitter.split(full_path)

        all_chunks.extend(file_chunks)

    # ========== EMBED CONTENTS =============

    model = LocalEmbeddingModel()

    embeddings = model.embed_documents(
        [chunk["chunk_content"] for chunk in all_chunks]
    )

    # ========== CREATE CHROMA DB =============

    store = VectorStore()

    store.add_chunks(chunks=all_chunks, vectors=embeddings)


if __name__ == "__main__":
    run_ingestion()