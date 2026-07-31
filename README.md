# 🚀 AI RAG Expert

A production-grade Retrieval-Augmented Generation (RAG) platform built with **FastAPI**, **Morphic**, **Qdrant**, **PostgreSQL**, and **Redis**.

The goal of this project is to build an enterprise-ready AI assistant capable of answering questions from private company documents while providing grounded, cited, and reliable responses.

---

## ✨ Project Goals

* Production-ready RAG architecture
* Enterprise document search
* Hybrid retrieval (Vector + Keyword)
* Multi-user support
* Source citations
* Agentic workflows
* Evaluation & Monitoring
* Docker-first deployment

---

# 🏗️ Architecture

```text
                Morphic (Next.js)

                       │

                       ▼

                 FastAPI Backend

        ┌──────────┬──────────┬──────────┐
        │          │          │          │
        ▼          ▼          ▼          ▼

   PostgreSQL    Qdrant     Redis     LLM
```

---

# 🛠️ Tech Stack

### Frontend

* Morphic
* Next.js

### Backend

* FastAPI
* Python 3.12

### AI

* LangGraph (planned)
* BGE-M3 Embeddings (planned)
* Qdrant

### Databases

* PostgreSQL
* Redis

### Deployment

* Docker
* Docker Compose

---

# 📂 Project Structure

```text
production-rag/

├── frontend/
│   └── morphic/
│
├── backend/
│   ├── app/
│   ├── uploads/
│   ├── tests/
│   └── Dockerfile
│
├── docker-compose.yml
├── .env
└── README.md
```

---

# ✅ Current Progress

### Infrastructure

* [x] Repository initialized
* [x] Morphic installed
* [x] FastAPI project initialized
* [x] Docker Compose configured
* [x] PostgreSQL container
* [x] Redis container
* [x] Qdrant container
* [x] Backend Docker container
* [x] Initial project architecture

---

# 🚧 Roadmap

## Phase 1 — Infrastructure ✅

* Docker Compose
* FastAPI
* Morphic
* PostgreSQL
* Redis
* Qdrant

---

## Phase 2 — Document Ingestion

* PDF Upload
* DOCX Upload
* Markdown
* Metadata Storage

---

## Phase 3 — Parsing & Chunking

* PDF Parsing
* Smart Chunking
* Metadata Extraction

---

## Phase 4 — Embeddings

* BGE-M3
* Vector Generation
* Qdrant Indexing

---

## Phase 5 — Retrieval

* Semantic Search
* Hybrid Search
* Metadata Filtering

---

## Phase 6 — Answer Generation

* Prompt Builder
* Citation Support
* Hallucination Guard

---

## Phase 7 — Agentic RAG

* LangGraph
* Query Rewriting
* Tool Calling

---

## Phase 8 — Evaluation

* RAGAS
* DeepEval
* Faithfulness
* Recall
* Precision

---

## Phase 9 — Production Features

* Authentication
* Multi-user
* Logging
* Monitoring
* Feedback
* Admin Dashboard

---

## Phase 10 — Deployment

* Kubernetes
* GitHub Actions
* CI/CD
* Observability

---

# 🚀 Running the Project

Start all services:

```bash
docker compose up -d
```

Backend:

```bash
http://localhost:8000/docs
```

Frontend:

```bash
http://localhost:3000
```

Qdrant Dashboard:

```bash
http://localhost:6333/dashboard
```

---

# 📌 Vision

The objective is not to build another "Chat with PDF" demo.

This project aims to become a production-grade enterprise RAG platform with robust retrieval, evaluation, monitoring, security, and scalable deployment following modern AI engineering best practices.

---

# 📄 License

MIT License
