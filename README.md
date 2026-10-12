# AI RAG Expert MCP Integreation

AI RAG Expert is an end-to-end Retrieval-Augmented Generation (RAG) system for interacting with uploaded documents through a conversational interface.

The system combines document ingestion, semantic search, conversational query rewriting, vector storage, and local LLM inference to generate grounded answers with source references.

---

## 🏗️ Architecture

```text
                              ┌─────────────────────┐
                              │      Gradio UI      │
                              │                     │
                              │  • Chat Interface   │
                              │  • File Upload      │
                              │  • Document Manager │
                              │  • Source Display   │
                              └──────────┬──────────┘
                                         │
                              Question + Chat History
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │      RAGService     │
                              │                     │
                              │   Main Orchestrator │
                              └──────────┬──────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │                                         │
                    ▼                                         ▼
          ┌─────────────────────┐                   ┌─────────────────────┐
          │   Query Rewriter    │                   │    Chat History     │
          │                     │                   │                     │
          │ Uses conversation   │                   │ Passed directly to  │
          │ history to resolve │                   │ the LLM for         │
          │ contextual queries  │                   │ conversational      │
          └──────────┬──────────┘                   │ understanding       │
                     │                              └──────────┬──────────┘
                     │                                         │
                     ▼                                         │
              Standalone Query                                 │
                     │                                         │
                     ▼                                         │
          ┌─────────────────────┐                              │
          │  Embedding Service  │                              │
          └──────────┬──────────┘                              │
                     │                                         │
                     ▼                                         │
          ┌─────────────────────┐                              │
          │       Qdrant        │                              │
          │                     │                              │
          │   Vector Search     │                              │
          └──────────┬──────────┘                              │
                     │                                         │
                     ▼                                         │
          ┌─────────────────────┐                              │
          │   Retrieved Chunks  │                              │
          └──────────┬──────────┘                              │
                     │                                         │
                     ▼                                         │
          ┌─────────────────────┐                              │
          │   Context Builder   │                              │
          └──────────┬──────────┘                              │
                     │                                         │
                     └──────────────────┬──────────────────────┘
                                        │
                                        ▼
                              ┌─────────────────────┐
                              │       Ollama        │
                              │                     │
                              │  System Prompt      │
                              │  + Chat History     │
                              │  + Retrieved Context│
                              │  + Current Question │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │   Answer + Sources  │
                              └──────────┬──────────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │  Gradio UI  │
                                  └─────────────┘
```

---

# 📄 Document Ingestion Pipeline

Before documents can be queried, they pass through an ingestion pipeline.

```text
             Uploaded Document
                     │
                     ▼
          ┌─────────────────────┐
          │  Document Service   │
          │                     │
          │  • Validation       │
          │  • File Storage     │
          │  • Database Record  │
          └──────────┬──────────┘
                     │
                     ▼
             ┌───────────────┐
             │    Parser     │
             │               │
             │ PDF / DOCX    │
             │ TXT / etc.    │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │    Chunker    │
             │               │
             │ Document      │
             │      ↓        │
             │ Text Chunks   │
             └───────┬───────┘
                     │
                     ▼
          ┌─────────────────────┐
          │  Metadata Builder   │
          │                     │
          │  • document_id     │
          │  • chunk_id        │
          │  • filename        │
          │  • chunk_index     │
          │  • page            │
          │  • section         │
          │  • created_at      │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │  Embedding Service  │
          │                     │
          │  Text → Vectors     │
          └──────────┬──────────┘
                     │
                     ▼
              ┌─────────────┐
              │   Qdrant   │
              │             │
              │ Vector      │
              │ + Text      │
              │ + Metadata  │
              └─────────────┘
```

---

# 🔍 Retrieval Pipeline

When a user asks a question, the system first transforms the question into a retrieval-friendly query.

```text
User Question
      │
      ▼
Chat History
      │
      ▼
Query Rewriter
      │
      ▼
Standalone Retrieval Query
      │
      ▼
Embedding
      │
      ▼
Qdrant Vector Search
      │
      ▼
Top-K Relevant Chunks
      │
      ▼
Context Builder
      │
      ▼
Retrieved Context
```

### Example

```text
Conversation:

User:
What is DEJEMUL-GATOR?

Assistant:
DEJEMUL-GATOR is a demulsifier.

User:
Who produces it?
```

The Query Rewriter transforms the contextual question:

```text
Who produces it?
```

into:

```text
Who produces DEJEMUL-GATOR?
```

The standalone query is then embedded and sent to Qdrant for retrieval.

---

# 💬 Conversational RAG

Chat history is maintained by the Gradio chat session.

The history is used in **two places**:

### 1. Query Rewriting

The history helps the Query Rewriter understand contextual references:

```text
it
this
that
they
he
she
```

and convert them into standalone retrieval queries.

### 2. Final Answer Generation

The same conversation history is passed directly to Ollama through its chat interface.

```text
System Prompt
      +
Conversation History
      +
Retrieved Context
      +
Current Question
      ↓
    Ollama
      ↓
    Answer
```

This allows the LLM to maintain conversational continuity while also grounding its answer in retrieved documents.

---

# 🧠 RAG Generation Flow

The final generation process combines conversational information with retrieved document context.

```text
                    ┌──────────────────┐
                    │   System Prompt  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Chat History    │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │ Retrieved Context│
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │ Current Question │
                    └────────┬─────────┘
                             │
                             ▼
                       ┌───────────┐
                       │  Ollama   │
                       │ Chat API  │
                       └─────┬─────┘
                             │
                             ▼
                           Answer
```

---

# 🗄️ Data Architecture

The application uses PostgreSQL for document-level persistence and Qdrant for vector storage.

```text
                    PostgreSQL
                         │
                         │
                  Document Records
                         │
                         │
                         ▼
                    document_id
                         │
                         │
                         ▼
                      Qdrant
                         │
              ┌──────────┴──────────┐
              │                     │
           Vector                 Payload
              │                     │
              │              ┌──────┴──────────┐
              │              │                 │
              │             text          document_id
              │                           filename
              │                           chunk_id
              │                           chunk_index
              │                           metadata
              │
              └───────────────► Retrieval
```

---

# 📦 Qdrant Payload

Each stored chunk contains both its vector representation and metadata.

```python
{
    "text": "...",
    "document_id": "...",
    "filename": "...",
    "chunk_id": "...",
    "chunk_index": 0,
    "page": None,
    "section": None,
    "created_at": "..."
}
```

This allows retrieved chunks to be traced back to their original document and displayed as sources in the UI.

---

# 🧩 Core Components

| Component             | Responsibility                                                    |
| --------------------- | ----------------------------------------------------------------- |
| **Gradio**            | Chat interface, file uploads, document management, source display |
| **RAGService**        | Orchestrates the complete RAG pipeline                            |
| **QueryRewriter**     | Converts contextual questions into standalone retrieval queries   |
| **Retriever**         | Performs semantic retrieval                                       |
| **QdrantService**     | Manages vector storage and similarity search                      |
| **ContextBuilder**    | Converts retrieved chunks into LLM context                        |
| **PromptBuilder**     | Defines system instructions and generation structure              |
| **LLMService**        | Interfaces with Ollama                                            |
| **Embedding Service** | Converts text into vector representations                         |
| **Ingestion Service** | Coordinates document ingestion                                    |
| **Parser**            | Extracts text from uploaded documents                             |
| **Chunker**           | Splits documents into chunks                                      |
| **MetadataBuilder**   | Generates chunk-level metadata                                    |
| **PostgreSQL**        | Stores document records and application metadata                  |

---

# 🛠️ Technology Stack

```text
Python
│
├── Gradio
│      └── Web UI / Chat
│
├── PostgreSQL
│      └── Document Metadata
│
├── Qdrant
│      └── Vector Database
│
├── Ollama
│      └── Local LLM Inference
│
├── Embedding Model
│      └── Semantic Representations
│
├── FastAPI
│      └── Application/API Components
│
└── Docker
       └── Infrastructure
```

---

# 🔄 Complete End-to-End Flow

```text
                         DOCUMENT INGESTION
                                │
                                ▼
                         Upload Document
                                │
                                ▼
                            Validation
                                │
                                ▼
                             Parsing
                                │
                                ▼
                            Chunking
                                │
                                ▼
                           Metadata
                                │
                                ▼
                           Embeddings
                                │
                                ▼
                             Qdrant
                                │
                                │
════════════════════════════════╪════════════════════════════════
                                │
                                │
                         USER QUERY
                                │
                                ▼
                         User Question
                                │
                                ▼
                          Chat History
                                │
                   ┌────────────┴────────────┐
                   │                         │
                   ▼                         ▼
             Query Rewriter              Ollama
                   │                         ▲
                   ▼                         │
            Standalone Query                │
                   │                         │
                   ▼                         │
              Embedding                     │
                   │                         │
                   ▼                         │
                Qdrant                      │
                   │                         │
                   ▼                         │
             Top-K Chunks                   │
                   │                         │
                   ▼                         │
             Context Builder                │
                   │                         │
                   └───────────┬─────────────┘
                               │
                               ▼
                             Ollama
                               │
                               ▼
                         Generated Answer
                               │
                         ┌─────┴─────┐
                         ▼           ▼
                      Answer       Sources
                         │           │
                         └─────┬─────┘
                               ▼
                           Gradio UI
```

---

# 📊 Evaluation

AI RAG Expert includes an evaluation pipeline covering **retrieval quality**, **answer quality**, and **failure analysis**.

## Retrieval Evaluation

Retrieval performance is measured using Recall@K, which evaluates whether the expected document chunk appears within the top-K retrieved results.

| Metric       | Description                                       |
| ------------ | ------------------------------------------------- |
| **Recall@1** | Expected chunk retrieved as the top result        |
| **Recall@3** | Expected chunk retrieved within the top 3 results |
| **Recall@5** | Expected chunk retrieved within the top 5 results |

Current retrieval results:

| Metric       |       Score |
| ------------ | ----------: |
| **Recall@1** |  **66.67%** |
| **Recall@3** |  **86.67%** |
| **Recall@5** | **100.00%** |

The results show that the correct chunk was retrieved within the top 5 results for all evaluation questions.

---

## RAG Answer Evaluation

The generated answers are evaluated across four dimensions:

| Metric               |      Score |
| -------------------- | ---------: |
| **Keyword Coverage** | **71.67%** |
| **Correctness**      | **86.00%** |
| **Relevance**        | **86.67%** |
| **Faithfulness**     | **83.33%** |

### Metrics

**Keyword Coverage**
Measures how many expected keywords from the reference answer appear in the generated answer.

**Correctness**
Measures whether the generated answer correctly addresses the expected answer.

**Relevance**
Measures whether the generated answer directly addresses the user's question.

**Faithfulness**
Measures whether the generated answer is supported by the retrieved context rather than introducing unsupported information.

---

## 🔬 Error Analysis

The evaluation pipeline also categorizes failed questions to identify where errors occur in the RAG pipeline.

```text
Total Questions       : 15
Success               : 7

Retrieval Failures    : 1
Retrieval Ranking     : 1
Generation Failures   : 1
Faithfulness Failures : 5
```

### Failure Categories

| Category                 | Description                                                                                    |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| **Retrieval Failure**    | The expected information was not retrieved                                                     |
| **Retrieval Ranking**    | The correct chunk was retrieved but ranked too low                                             |
| **Generation Failure**   | Retrieved information was available but the generated answer was incorrect or incomplete       |
| **Faithfulness Failure** | The generated answer contained information not sufficiently supported by the retrieved context |

---

## 🧪 Detailed Failure Analysis

For failed questions, the evaluation system reports:

* Original question
* Failure category
* Explanation
* Expected answer
* Generated answer
* Correct chunk rank
* Correctness score
* Relevance score
* Faithfulness score

This makes it possible to distinguish between **retrieval problems** and **generation problems**, rather than treating every incorrect answer as a single type of failure.

### Example Analysis Flow

```text
Question
   │
   ▼
Retrieval
   │
   ├── Correct chunk not found
   │       └── Retrieval Failure
   │
   ├── Correct chunk found but ranked low
   │       └── Retrieval Ranking
   │
   └── Correct context retrieved
           │
           ▼
        Generation
           │
           ├── Incorrect answer
           │       └── Generation Failure
           │
           └── Unsupported claim
                   └── Faithfulness Failure
```

The evaluation framework is designed to be extensible as retrieval and generation components evolve.


# 🚧 Future Improvements

The current architecture can be extended with:

* Hybrid retrieval (Dense + BM25)
* Cross-encoder reranking
* Advanced query transformation
* Improved chunking strategies
* Retrieval evaluation
* Generation evaluation
* RAG observability and tracing
* Streaming LLM responses
* Production deployment and scaling
