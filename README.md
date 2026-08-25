# 🚀 AI RAG Expert

AI RAG Expert is a production-oriented Retrieval-Augmented Generation (RAG) platform for intelligent question answering over private documents.

The system provides a complete document-to-answer pipeline: documents are validated, stored, parsed, chunked, embedded, indexed in Qdrant, retrieved based on semantic similarity, and finally passed as grounded context to a local LLM through Ollama.

The project is designed with modular AI engineering and production-oriented architecture in mind, with a clear path toward advanced retrieval, evaluation, observability, authentication, and scalable deployment.

---

## 🎯 Overview

AI RAG Expert allows users to upload private documents and ask questions about their content.

Instead of relying only on the knowledge stored inside an LLM, the system retrieves relevant information from the user's documents and provides that information to the model as context.

### Question Answering Pipeline

```text
                    User
                     │
                     ▼
               User Question
                     │
                     ▼
              Embedding Model
                     │
                     ▼
                Qdrant Search
                     │
                     ▼
              Relevant Chunks
                     │
                     ▼
              Context Builder
                     │
                     ▼
              Prompt Builder
                     │
                     ▼
                  Ollama
                     │
                     ▼
              Grounded Answer
````

### Document Ingestion Pipeline

```text
              Document Upload
                     │
                     ▼
              File Validation
                     │
                     ▼
               File Storage
                     │
                     ▼
                PostgreSQL
                     │
                     ▼
              Document Parser
                     │
                     ▼
                  Chunking
                     │
                     ▼
                Embeddings
                     │
                     ▼
                  Qdrant
```

---

# ✨ Key Features

* 📄 PDF, DOCX, TXT and Markdown document ingestion
* 🔍 Semantic vector search
* 🧠 Embedding-based retrieval
* 🤖 Local LLM inference using Ollama
* 🗄️ PostgreSQL document metadata management
* 🔎 Qdrant vector database
* 🧩 Modular parsing and chunking pipeline
* 📝 Context-aware prompt construction
* 🔗 Document-level chunk management using `document_id`
* 🗑️ Document deletion across Qdrant, PostgreSQL and file storage
* 🌐 FastAPI backend
* 💬 Gradio interface
* 🧪 Automated testing with Pytest
* 🐳 Docker-based infrastructure
* 🔐 Architecture prepared for multi-user support
* 📊 Designed for future evaluation and monitoring

---

# 🏗️ Architecture

```text
                         ┌─────────────────┐
                         │     Gradio      │
                         │   User Interface│
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     FastAPI     │
                         │    Backend      │
                         └────────┬────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
             ┌───────────┐ ┌───────────┐ ┌───────────┐
             │ PostgreSQL│ │  Qdrant   │ │  Ollama   │
             │ Metadata  │ │  Vectors  │ │    LLM    │
             └───────────┘ └───────────┘ └───────────┘
                    │             │
                    └──────┬──────┘
                           ▼
                     RAG Service
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
            Retriever          Context Builder
                                      │
                                      ▼
                               Prompt Builder
                                      │
                                      ▼
                                   Ollama
```

---

# 🧠 RAG Architecture

The RAG system is divided into independent services.

## Document Ingestion

The ingestion pipeline handles the complete lifecycle of an uploaded document:

```text
Upload
  │
  ▼
Validation
  │
  ▼
Storage
  │
  ▼
PostgreSQL Record
  │
  ▼
Parsing
  │
  ▼
Chunking
  │
  ▼
Embedding
  │
  ▼
Qdrant
```

Each document receives a unique `document_id`.

This ID is used to associate every chunk with its original document.

---

## Retrieval

When a user asks a question:

```text
Question
   │
   ▼
Embedding
   │
   ▼
Query Vector
   │
   ▼
Qdrant
   │
   ▼
Top-K Similar Chunks
```

The retriever returns the most semantically relevant chunks.

Each chunk contains metadata such as:

```json
{
  "document_id": "647a9a57-1a57-4978-84aa-0176848015bb",
  "filename": "resume.pdf",
  "chunk_index": 3,
  "text": "AI Engineer with experience in..."
}
```

---

# 🧩 Context Builder

The retrieved chunks are transformed into a structured context for the LLM.

Example:

```text
[Source 1]
File: resume.pdf
Chunk: 3
AI Engineer with experience in...

[Source 2]
File: resume.pdf
Chunk: 5
Experience with FastAPI and Qdrant...
```

This gives the LLM explicit source boundaries and document metadata.

---

# 📝 Prompt Builder

The prompt builder combines:

* System instructions
* Retrieved context
* User question

The LLM is instructed to answer only using the supplied context.

If the required information cannot be found, the model is instructed to state that there is not enough information rather than inventing an answer.

---

# 🤖 LLM

The project uses **Ollama** for local LLM inference.

This provides:

* Local inference
* No dependency on external LLM APIs
* Greater control over data privacy
* Ability to switch between locally available models

Example:

```text
Context + Question
        │
        ▼
      Ollama
        │
        ▼
      Answer
```

---

# 🗄️ Data Architecture

## PostgreSQL

PostgreSQL stores document metadata and document lifecycle information.

Example:

```text
documents
├── id
├── filename
├── stored_name
├── path
├── extension
├── mime_type
├── size
├── category
├── status
└── created_at
```

---

## Qdrant

Qdrant stores vector representations of document chunks.

Each point contains both the vector and metadata:

```json
{
  "document_id": "647a9a57-1a57-4978-84aa-0176848015bb",
  "filename": "resume.pdf",
  "chunk_index": 0,
  "text": "..."
}
```

The `document_id` is the connection between PostgreSQL and Qdrant.

This makes document-level operations possible without relying on filenames.

---

# 🗑️ Document Lifecycle

A document is treated as a single logical entity even though its data is distributed across multiple systems.

### Upload

```text
                 Document
                     │
                     ▼
                Validation
                     │
                     ▼
                 File Store
                     │
                     ▼
                PostgreSQL
                     │
                     ▼
              Parse + Chunk
                     │
                     ▼
                Embeddings
                     │
                     ▼
                  Qdrant
```

### Delete

```text
                document_id
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Qdrant    PostgreSQL   Storage
       Chunks      Record       File
          │          │          │
          └──────────┴──────────┘
                     │
                     ▼
                Document Gone
```

This prevents orphaned vectors, database records, or physical files.

---

# 🛠️ Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic

### AI / RAG

* Ollama
* Qdrant
* Embedding Models
* Retrieval-Augmented Generation
* Prompt Engineering

### Databases

* PostgreSQL
* Qdrant
* Redis

### Frontend / Interface

* Gradio

### Infrastructure

* Docker
* Docker Compose

### Testing

* Pytest

---

# 📂 Project Structure

```text
AI-RAG-Expert/
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   ├── database/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   └── services/
│   │
│   ├── tests/
│   ├── uploads/
│   ├── gradio_app.py
│   ├── main.py
│   └── Dockerfile
│
├── docker-compose.yml
├── .env
└── README.md
```

---

# 🧪 Testing

The project uses Pytest to test individual components and the complete RAG pipeline.

Current tests cover:

* Context Builder
* Prompt Builder
* Document Repository
* Qdrant connectivity
* Retriever
* LLM generation
* RAG pipeline

Run the tests:

```bash
cd backend

python -m pytest -v
```

---

# 🚀 Running the Project

## 1. Start infrastructure

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

The infrastructure includes:

* PostgreSQL
* Qdrant
* Redis

---

## 2. Start the Backend

Activate the virtual environment:

```bash
source venv/bin/activate
```

Run FastAPI:

```bash
uvicorn main:app --reload
```

API documentation:

```text
http://localhost:8000/docs
```

---

## 3. Start Ollama

Run Ollama locally:

```bash
ollama serve
```

Pull a model:

```bash
ollama pull llama3.1
```

---

## 4. Start Gradio

```bash
python gradio_app.py
```

The interface will be available at:

```text
http://127.0.0.1:7860
```

---

# 📊 Current Development Status

| Component             | Status        |
| --------------------- | ------------- |
| Infrastructure        | ✅ Complete    |
| Docker Compose        | ✅ Complete    |
| PostgreSQL            | ✅ Complete    |
| Qdrant                | ✅ Complete    |
| Redis                 | 🟢 Configured |
| File Storage          | ✅ Complete    |
| File Validation       | ✅ Complete    |
| Document Parsing      | ✅ Complete    |
| Chunking              | ✅ Complete    |
| Ingestion Pipeline    | ✅ Complete    |
| Embeddings            | 🟢 Functional |
| Qdrant Indexing       | 🟢 Functional |
| Semantic Retrieval    | 🟢 Functional |
| Context Builder       | ✅ Complete    |
| Prompt Builder        | ✅ Complete    |
| Ollama Integration    | ✅ Complete    |
| RAG Pipeline          | ✅ Functional  |
| Document Deletion     | 🟢 Functional |
| FastAPI API           | 🟢 Functional |
| Gradio UI             | 🟢 Functional |
| Hybrid Search         | 🚧 Planned    |
| Evaluation            | 🚧 Planned    |
| Authentication        | 🚧 Planned    |
| Monitoring            | 🚧 Planned    |
| Production Deployment | 🚧 Planned    |

---

# 🗺️ Roadmap

## Phase 1 — Core RAG ✅

* [x] Document ingestion
* [x] File validation
* [x] Parsing
* [x] Chunking
* [x] Embeddings
* [x] Qdrant indexing
* [x] Semantic retrieval
* [x] Context construction
* [x] Prompt construction
* [x] Local LLM generation
* [x] End-to-end RAG pipeline

## Phase 2 — Document Management ✅

* [x] Document upload
* [x] Document listing
* [x] Document metadata
* [x] Document deletion
* [x] Qdrant document-level filtering
* [x] PostgreSQL document lifecycle

## Phase 3 — Advanced Retrieval

* [ ] Hybrid vector + keyword retrieval
* [ ] Metadata filtering
* [ ] Query expansion
* [ ] Query rewriting
* [ ] Reranking
* [ ] Retrieval evaluation

## Phase 4 — Answer Quality

* [ ] Source citations
* [ ] Faithfulness evaluation
* [ ] Context precision
* [ ] Context recall
* [ ] Answer relevance
* [ ] RAGAS
* [ ] DeepEval

## Phase 5 — Production Features

* [ ] Authentication
* [ ] Multi-user support
* [ ] Document-level access control
* [ ] Redis caching
* [ ] Background ingestion jobs
* [ ] Logging
* [ ] Metrics
* [ ] Observability
* [ ] Rate limiting
* [ ] Feedback system

## Phase 6 — Deployment

* [ ] Production Docker images
* [ ] CI/CD
* [ ] GitHub Actions
* [ ] Kubernetes
* [ ] Horizontal scaling
* [ ] Production monitoring

---

# 🎯 Project Vision

AI RAG Expert is built to demonstrate the engineering of a complete RAG system rather than simply wrapping an LLM API.

The project focuses on the complete lifecycle of enterprise document intelligence:

```text
             Documents
                 │
                 ▼
             Ingestion
                 │
                 ▼
             Processing
                 │
                 ▼
             Chunking
                 │
                 ▼
             Embeddings
                 │
                 ▼
          Vector Storage
                 │
                 ▼
             Retrieval
                 │
                 ▼
       Context Construction
                 │
                 ▼
         Prompt Engineering
                 │
                 ▼
          Local LLM
                 │
                 ▼
        Grounded Answers
                 │
                 ▼
          Evaluation
                 │
                 ▼
          Production
```

The long-term objective is to evolve the system into a scalable enterprise knowledge platform capable of working with private organizational data while maintaining reliable retrieval, grounded generation, traceability, and operational visibility.

---

# 🔐 Privacy

The architecture supports local document processing and local LLM inference.

Documents can remain within the application's infrastructure while embeddings, metadata, and vector representations are managed by self-hosted services.

---

# 📄 License

This project is licensed under the **Apache License 2.0**.

See the `LICENSE` file for the complete license text.

