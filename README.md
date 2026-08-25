# AI Codebase Intelligence

AI Codebase Intelligence is a backend system for indexing, searching, and understanding software repositories using retrieval-augmented generation (RAG).

Instead of sending an entire codebase to an LLM, the system ingests source files, splits them into searchable chunks, extracts structured code information, creates semantic embeddings, and retrieves only the code relevant to a question.

The retrieval pipeline combines BM25 lexical search, semantic vector search, Reciprocal Rank Fusion (RRF), and cross-encoder reranking before passing the final context to a local LLM.

The project also exposes read-only MCP tools so compatible AI clients can interact with an indexed codebase directly.

---

## Architecture

```text
Repository
    |
    v
Ingestion
    |
    v
Chunking + Structured Metadata
    |
    +-----------------------+
    |                       |
    v                       v
BM25 Search          Semantic Embeddings
                            |
                            v
                         Pinecone
    |                       |
    +-----------+-----------+
                |
                v
       Reciprocal Rank Fusion
                |
                v
       Cross-Encoder Reranker
                |
                v
          Relevant Context
                |
                v
             Ollama
                |
                v
      Grounded Answer + Citations
```

Background repository indexing runs separately:

```text
FastAPI
   |
   v
 Redis
   |
   v
Celery Worker
   |
   +--> Ingestion
   +--> Chunking
   +--> Metadata Extraction
   +--> Embedding / Indexing
```

Redis is also used to cache repeated RAG queries.

---

## Features

- FastAPI REST API
- PostgreSQL persistence
- JWT authentication
- Password hashing
- Repository ingestion
- Source-code chunking
- Structured code metadata extraction
- Semantic embeddings
- Pinecone vector search
- BM25 lexical retrieval
- Reciprocal Rank Fusion (RRF)
- Cross-encoder reranking
- Retrieval-augmented generation
- File and line-range citations
- Local LLM inference with Ollama
- Redis response caching
- Celery background indexing
- Background job status tracking
- MCP server
- Read-only MCP tools
- Retrieval evaluation
- Automated tests
- Docker Compose development environment

---

## Retrieval Pipeline

The system uses several retrieval stages rather than relying on a single vector search.

### BM25

BM25 provides lexical retrieval and is useful when a question contains exact identifiers, function names, or terminology from the source code.

### Semantic Search

Source-code chunks are converted into embeddings and indexed in Pinecone.

Queries are embedded using the same embedding model and matched against indexed code.

Semantic retrieval allows the system to find relevant code even when the question does not contain the exact words used by the implementation.

### Reciprocal Rank Fusion

BM25 and semantic results are combined using Reciprocal Rank Fusion.

RRF works with the rank position of results rather than trying to directly compare BM25 scores with vector similarity scores.

### Cross-Encoder Reranking

The fused candidate set is passed through a cross-encoder reranker.

Unlike embedding similarity, the reranker evaluates the query and candidate together before producing the final ranking.

The final top results are used as context for the LLM.

---

## Retrieval Evaluation

I created a small ground-truth evaluation set and compared the retrieval approaches using Hit@5 and MRR@5.

| Retrieval Method | Hit@5 | MRR@5 |
| --- | ---: | ---: |
| BM25 | 0.750 | 0.500 |
| Semantic | 1.000 | 0.854 |
| Hybrid RRF | 0.875 | 0.692 |
| RRF + Reranker | **1.000** | **0.875** |

The evaluation showed that semantic retrieval initially performed better than equal-weight RRF.

This was important because it showed that adding more retrieval techniques did not automatically improve the system.

Adding a cross-encoder reranker improved MRR@5 from `0.854` for semantic retrieval to `0.875` while maintaining a Hit@5 of `1.000`.

Based on these results, the final RAG pipeline uses reranked retrieval.

---

## RAG

The RAG endpoint follows this pipeline:

```text
Question
   |
   v
BM25 + Semantic Retrieval
   |
   v
RRF Candidate Fusion
   |
   v
Cross-Encoder Reranking
   |
   v
Top Code Chunks
   |
   v
Prompt Construction
   |
   v
Local LLM
   |
   v
Answer + Source Metadata
```

The LLM is instructed to answer using only retrieved code context and to avoid inventing files, functions, classes, or behavior that are not present in that context.

The response contains information about the source files, line ranges, and chunks used during generation.

---

## Background Processing

Repository indexing can be expensive because it may involve:

- Reading many source files
- Chunking source code
- Extracting structured metadata
- Generating embeddings
- Sending vectors to Pinecone

These operations are processed asynchronously using Celery.

FastAPI creates an indexing job and immediately returns a job ID. Redis acts as the Celery broker and result backend, while a separate worker performs the indexing pipeline.

Clients can use the job status endpoint to check the progress and result of an indexing operation.

```text
Request
   |
   v
FastAPI
   |
   v
Job ID returned
   |
   +------------------------+
                            |
                            v
                          Redis
                            |
                            v
                      Celery Worker
                            |
                            v
                Repository Processing
```

This keeps expensive repository processing outside the HTTP request lifecycle.

---

## Caching

Redis is also used to cache RAG responses.

Cache keys are generated using the repository, normalized query, and retrieval configuration.

The first request runs the complete pipeline:

```text
Question
   |
   v
Cache Miss
   |
   v
Retrieval
   |
   v
Reranking
   |
   v
LLM
   |
   v
Store in Redis
```

An identical request can then use:

```text
Question
   |
   v
Cache Hit
   |
   v
Cached Response
```

Cached responses have a TTL so they expire automatically.

---

## MCP

The project includes a Model Context Protocol (MCP) server that exposes codebase intelligence capabilities to compatible AI clients.

Available tools include:

### `search_code`

Searches an indexed repository using the retrieval system.

### `get_file`

Retrieves the contents of an indexed source file.

### `list_symbols`

Returns structured symbols extracted from the repository.

### `ask_codebase`

Runs a grounded RAG question against an indexed repository.

The MCP interface is intentionally read-only.

It does not expose arbitrary shell execution, unrestricted file modification, or repository deletion.

This allows an AI client to inspect and reason about a repository without giving it unnecessary write access.

---

## Authentication

Users authenticate using JWT bearer tokens.

Passwords are hashed before being stored.

After a successful login, the API generates an expiring JWT containing the user's ID.

Protected endpoints decode the token and load the corresponding user before allowing access to repository resources.

JWT secrets and other credentials are loaded from environment variables rather than being stored directly in the source code.

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Alembic

### AI and Retrieval

- Sentence Transformers
- Pinecone
- BM25
- Reciprocal Rank Fusion
- Cross-Encoder reranking
- Ollama

### Infrastructure

- Docker
- Docker Compose
- Redis
- Celery

### Integration

- Model Context Protocol (MCP)

### Testing and Evaluation

- Pytest
- Hit@5
- MRR@5

---

## Project Structure

```text
ai-codebase-intelligence/
|
|-- app/
|   |
|   |-- api/
|   |   |-- auth.py
|   |   |-- dependencies.py
|   |   |-- jobs.py
|   |   |-- rag.py
|   |   |-- search.py
|   |
|   |-- core/
|   |   |-- celery_app.py
|   |   |-- config.py
|   |   |-- database.py
|   |   |-- security.py
|   |
|   |-- mcp/
|   |   |-- server.py
|   |
|   |-- models/
|   |
|   |-- repositories/
|   |
|   |-- schemas/
|   |
|   |-- services/
|   |   |-- auth.py
|   |   |-- bm25_search.py
|   |   |-- cache.py
|   |   |-- chunking.py
|   |   |-- hybrid_search.py
|   |   |-- ingestion.py
|   |   |-- llm.py
|   |   |-- metadata_extraction.py
|   |   |-- rag.py
|   |   |-- reranker.py
|   |   |-- reranked_search.py
|   |   |-- semantic_search.py
|   |
|   |-- tasks/
|   |   |-- repository_indexing.py
|   |
|   |-- main.py
|
|-- evaluation/
|   |-- retrieval_cases.json
|   |-- evaluate_retrieval.py
|
|-- tests/
|
|-- scripts/
|
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
|-- requirements-ai.txt
|-- .env.example
|-- README.md
```

---

## Running the Project

### Requirements

You need:

- Docker
- Docker Compose
- Ollama
- A Pinecone account and API key

---

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-codebase-intelligence
```

---

### 2. Configure Environment Variables

Create a `.env` file based on `.env.example`.

Configure the required values:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/codebase_intelligence

PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=codebase-intelligence

OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5-coder:3b

REDIS_URL=redis://redis:6379/0
RAG_CACHE_TTL_SECONDS=900

JWT_SECRET_KEY=your_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Do not commit `.env` or real credentials.

A JWT secret can be generated with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

### 3. Start Ollama

Pull the configured model if necessary:

```bash
ollama pull qwen2.5-coder:3b
```

Make sure Ollama is running before making RAG requests.

---

### 4. Start the Application

```bash
docker compose up --build -d
```

Check the containers:

```bash
docker compose ps
```

The stack contains:

```text
FastAPI API
PostgreSQL
Redis
Celery Worker
```

---

### 5. Open the API Documentation

Swagger UI is available at:

```text
http://localhost:8000/docs
```

The API can be used to register/login, manage repositories, search indexed code, run RAG queries, and start background indexing jobs.

---

## Background Indexing

Repository indexing can be submitted through the background job endpoint.

The API returns a job ID instead of waiting for the complete indexing pipeline to finish.

The job status endpoint can then be used to check whether the task is:

```text
PENDING
PROGRESS
SUCCESS
FAILURE
```

The Celery worker can be monitored with:

```bash
docker compose logs -f worker
```

---

## Tests

Run the automated tests inside Docker:

```bash
docker compose exec api pytest -q
```

The tests cover core functionality including authentication security behavior and retrieval-related logic.

---

## Retrieval Evaluation

Run the retrieval benchmark with:

```bash
docker compose exec api python -m evaluation.evaluate_retrieval
```

The evaluation compares:

```text
BM25
Semantic Search
Hybrid RRF
RRF + Cross-Encoder Reranking
```

using Hit@5 and MRR@5.

The measured results for the current evaluation set are:

```text
BM25       Hit@5=0.750 MRR@5=0.500
Semantic   Hit@5=1.000 MRR@5=0.854
Hybrid     Hit@5=0.875 MRR@5=0.692
Reranked   Hit@5=1.000 MRR@5=0.875
```

---

## MCP Development

The MCP server can be started with:

```bash
python -m app.mcp.server
```

It can also be inspected during development using MCP Inspector.

The server exposes:

```text
search_code
get_file
list_symbols
ask_codebase
```

These tools provide read-only access to indexed repository intelligence.

---

## Design Decisions

### Why use both BM25 and semantic retrieval?

Semantic retrieval is useful for questions where the wording differs from the source code.

BM25 is useful for exact technical terminology, identifiers, and function names.

Using both provides different candidate signals.

### Why use RRF?

BM25 scores and vector similarity scores are not directly comparable.

RRF combines ranked lists using their positions rather than attempting to normalize unrelated score types.

### Why add a reranker?

Evaluation showed that equal-weight RRF alone performed worse than semantic retrieval.

Instead of assuming the hybrid system was better, I measured it.

A cross-encoder reranker was then added to evaluate the query and candidate chunks together.

This improved MRR@5 from `0.854` for semantic retrieval to `0.875` while maintaining a Hit@5 of `1.000`.

### Why use background jobs?

Repository indexing involves operations that can take significantly longer than a normal API request.

Moving indexing into Celery allows FastAPI to return immediately while the worker handles the expensive processing separately.

### Why use Redis?

Redis serves two purposes:

1. Celery broker and result backend for background processing.
2. Cache for repeated RAG requests.

### Why use a local LLM?

Ollama allows the RAG pipeline to run without requiring a paid LLM API.

The LLM provider is kept separate from the retrieval pipeline so the generation layer can be changed independently.

### Why expose MCP tools?

MCP allows compatible AI clients to use the project's capabilities as tools instead of requiring every interaction to happen directly through REST endpoints.

The exposed tools are intentionally read-only to limit what an AI client can do.

---

## What I Learned

The main lesson from this project was that building a RAG system involves much more than connecting an embedding model to an LLM.

Retrieval quality had to be measured rather than assumed.

My initial equal-weight hybrid retrieval was more complex than semantic retrieval but performed worse on the evaluation set. Building an evaluation pipeline exposed that problem.

Adding cross-encoder reranking improved the final ranking and gave me a measurable reason to use the more complex retrieval pipeline.

I also had to think about the software around the AI components: authentication, persistence, asynchronous processing, caching, configuration, testing, API design, vector storage, and safe tool access.

The result is a system where the LLM is one component inside a larger backend architecture rather than the entire application.

---

## Current Retrieval Results

| Method | Hit@5 | MRR@5 |
| --- | ---: | ---: |
| BM25 | 0.750 | 0.500 |
| Semantic | 1.000 | 0.854 |
| Hybrid RRF | 0.875 | 0.692 |
| **RRF + Reranker** | **1.000** | **0.875** |

The reranked pipeline currently provides the best retrieval performance on the project's evaluation set.

---

## Security

- Passwords are hashed before storage.
- Protected endpoints require JWT authentication.
- JWT secrets are stored in environment configuration.
- Repository access is restricted to the owning user.
- `.env` is excluded from version control.
- MCP tools are read-only.
- The LLM is instructed to answer from retrieved context rather than unrestricted assumptions.

---

## Status

The core system is complete and includes:

```text
API
Database
Authentication
Repository ingestion
Background jobs
Semantic embeddings
Pinecone vector search
BM25
RRF
Cross-encoder reranking
RAG
Redis caching
Celery
MCP
Retrieval evaluation
Automated tests
Docker Compose
```