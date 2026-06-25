# EU Regulatory RAG Assistant

A Retrieval-Augmented Generation (RAG) system for querying EU regulatory documents (GDPR, DORA, NIS2, AI Act, Data Act, Data Governance Act, Open Data Directive, etc.). The project downloads official documents from **EUR-Lex**, splits them into chunks, embeds them locally, stores them in a **ChromaDB** vector store, and answers natural-language questions using an LLM (via **Groq**) grounded strictly in the retrieved context.

---

## Features

- **Automated Downloading** — Fetches legal documents directly from EUR-Lex by CELEX identifier, in HTML, TXT, or PDF format.
- **Document Splitting** — Splits PDFs and plain text documents into overlapping chunks using `RecursiveCharacterTextSplitter`, with metadata extraction (title, date, source URL).
- **Local Embeddings** — Uses `sentence-transformers` to generate embeddings without relying on external embedding APIs.
- **Vector Storage & Retrieval** — Persists embeddings in ChromaDB and retrieves relevant chunks using **Maximal Marginal Relevance (MMR)** reranking for diverse, relevant results.
- **Grounded Question Answering** — Uses a strict system prompt to ensure the LLM answers *only* from retrieved context, with mandatory source citations (document, page, date, URL).
- **Provenance Tracking** — Maps every downloaded CELEX document to its source URL in a JSON log for traceability.

---

## Architecture

```
EUR-Lex (Downloader)
        |
        v
Raw Documents (PDF/HTML/TXT)
        |
        v
Splitter (PDF / Text)
        |
        v
Chunks + Metadata
        |
        v
Local Embedding Model (SentenceTransformers)
        |
        v
ChromaDB Vector Store
        |
        v
Retriever (MMR search)
        |
        v
LLM (Groq) --> Answer + Sources
```

---

## Project Structure

```
.
├── docs/                          # Downloaded source documents
├── URL_LOGS/                      # JSON mapping of CELEX IDs to source URLs
├── Vector_DB_Folder/              # Persisted ChromaDB vector store
├── src/
│   ├── config.py                  # Central configuration (paths, chunking, models)
│   ├── Ingestion/
│   │   ├── downloader.py          # EUR-Lex downloader
│   │   ├── ingest.py              # Full ingestion process
│   │   ├── Splitters/
│   │   │   ├── splitter.py        # Base splitter class + metadata extraction
│   │   │   ├── pdf_splitter.py    # PDF-specific splitter
│   │   │   └── text_splitter.py   # Plain-text splitter
│   │   ├── Vectorization/
│   │   │   └── embedding_model.py # Local embedding model wrapper
│   │   └── DB/
│   │       └── vector_store.py    # ChromaDB wrapper + MMR search
│   ├── LLM/
│   │   ├── llm_factory.py         # Groq client factory
│   │   ├── system_prompt.py       # System prompt for grounded answers
│   │   └── retriever.py           # RAG pipeline (retrieve -> context -> answer)
│   ├── RAG.py                     # Ask questions
```

---

## Setup

### 1. Clone & install dependencies

```bash
git clone https://github.com/GiannisApostolopoulos/RAG-System-for-EU-Regulations-Compliance.git
cd RAG-System-for-EU-Regulations-Compliance
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
ENDPOINT=your_groq_endpoint
MODEL=your_model_name
```

### 3. Ingest documents into the vector database

```bash
python src/Ingestion/ingest.py
```

### 4. Ask questions

```bash
python src/rag.py
```

Or programmatically:

```python
from LLM.retriever import Retriever

retriever = Retriever()
result = retriever.ask("What is GDPR?")
print(result["clean_answer"])
```

---

## Configuration

All key parameters live in `src/config.py`:

| Variable | Description |
|---|---|
| `DOCS_DIR` | Directory for downloaded documents |
| `URL_LOGS` | Directory for the CELEX → URL mapping JSON |
| `VECTOR_DIR` | ChromaDB persistence directory |
| `CELEX_LIST` | Dictionary of regulation names → CELEX IDs to download |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | Text splitting parameters |
| `SEPARATORS` | Regex separators used for chunking (e.g. `Article`, numbered clauses) |
| `EMBEDDING_MODEL_NAME` | SentenceTransformers model used for embeddings |
| `N_RESULTS` / `FETCH_K` / `LAMBDA_MULT` | Retrieval and MMR reranking parameters |
| `TEMPERATURE` | LLM sampling temperature |

---

## How Answers Are Grounded

The system prompt (`LLM/system_prompt.py`) enforces:

- Answers **only** from retrieved context — no external knowledge or speculation.
- Explicit fallback message when context is insufficient.
- Mandatory, consistently formatted source citations (title, date, page, URL).
- Distinction between binding regulations, directives, and advisory guidelines.

---

## Future Improvements

- Implement HTML splitter
- Remove print messages from downloader 
- Add try-catch blocks  and logger in ingest.py
- Implement LLM as judge
- Interface (either webpage via FastAPI or mini app)
- Implement system prompt with specialized library instead of a simple string

---

