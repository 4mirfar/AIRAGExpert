import gradio as gr
from pathlib import Path
import uuid

from app.services.rag import RAGService
from app.services.embedding import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.storage import StorageService
from app.services.validation import FileValidationService
from app.services.ingestion import IngestionService
from app.services.document_service import DocumentService

from app.database.database import SessionLocal
from app.repositories.document_repository import DocumentRepository

import mimetypes


# ============================================================
# Services
# ============================================================

embedding_service = EmbeddingService()
qdrant_service = QdrantService()
validator = FileValidationService()
storage = StorageService()
ingestion_service = IngestionService()


rag_service = RAGService(
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
)


# ============================================================
# Database
# ============================================================

def get_documents():
    """
    Return documents for displaying in the UI.
    """

    db = SessionLocal()

    try:
        repository = DocumentRepository(db)

        documents = repository.get_all()

        return [
            {
                "id": str(document.id),
                "filename": document.filename,
                "status": document.status,
            }
            for document in documents
        ]

    finally:
        db.close()


# ============================================================
# UI document list
# ============================================================

def document_choices():
    """
    Return choices for the Gradio Radio component.
    """

    documents = get_documents()

    return [
        (
            f"{doc['filename']} ({doc['status']})",
            doc["id"],
        )
        for doc in documents
    ]


# ============================================================
# Delete document
# ============================================================

def delete_document(document_id):
    """
    Delete selected document from:

    1. Qdrant
    2. PostgreSQL
    3. Stored file
    """


    print("🔥 delete_document called")
    print("document_id:", repr(document_id))

    if not document_id:
        return (
            gr.update(
                choices=document_choices(),
                value=None,
            ),
            "⚠️ Select a document first.",
        )

    db = SessionLocal()

    try:
        repository = DocumentRepository(db)
        document_service = DocumentService(repository=repository,
                                            qdrant_service=qdrant_service)

        # ----------------------------------------------------
        # Find document
        # ----------------------------------------------------

        document = repository.get_by_id(document_id)

        if document is None:
            return (
                gr.update(
                    choices=document_choices(),
                    value=None,
                ),
                "❌ Document not found.",
            )

        # ----------------------------------------------------
        # Delete vectors from Qdrant and Database
        # ----------------------------------------------------
        # points, _ = qdrant_service.client.scroll(
        #     collection_name=qdrant_service.COLLECTION_NAME,
        #     limit=10,
        #     with_payload=True,
        #     with_vectors=False,
        # )

        # print("TOTAL:", len(points))

        # for point in points:
        #     print(point.payload)
        # print(len(qdrant_service.get_chunks_by_document_id(document_id=document_id)))

        document_service.delete_document(
            document_id=document_id
        )

        # ----------------------------------------------------
        # Delete physical file
        # ----------------------------------------------------

        file_path = Path(document.path)

        if file_path.exists():
            file_path.unlink()


        # ----------------------------------------------------
        # Refresh UI
        # ----------------------------------------------------

        return (
            gr.update(
                choices=document_choices(),
                value=None,
            ),
            f"✅ Deleted: {document.filename}",
        )

    except Exception as e:

        db.rollback()

        return (
            gr.update(
                choices=document_choices(),
                value=document_id,
            ),
            f"❌ Delete failed: {type(e).__name__}: {e}",
        )

    finally:
        db.close()


# ============================================================
# Upload
# ============================================================

async def upload_document(file):

    if file is None:
        return (
            gr.update(choices=document_choices(), value=None),
            "⚠️ Select a file.",
        )

    db = SessionLocal()

    try:
        # ----------------------------------------------------
        # 1. Get file path
        # ----------------------------------------------------

        if isinstance(file, str):
            file_path = Path(file)

        else:
            file_path = Path(file.name)

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        # ----------------------------------------------------
        # 2. Get filename
        # ----------------------------------------------------

        filename = file_path.name

        # ----------------------------------------------------
        # 3. Validate
        # ----------------------------------------------------

        await validator.validate(file_path)

        # ----------------------------------------------------
        # 4. Save file
        # ----------------------------------------------------

        # Your StorageService should accept Path.
        result = await storage.save_file(
            file=file_path,
            category="documents",
        )

        # ----------------------------------------------------
        # 5. Create database record
        # ----------------------------------------------------

        repository = DocumentRepository(db)

        document = repository.create(
            document_id=result["document_id"],
            filename=result["filename"],
            stored_name=result["stored_name"],
            path=result["path"],
            extension=Path(
                result["filename"]
            ).suffix.lower(),
            mime_type=mimetypes.guess_type(
                result["filename"]
            )[0] or "application/octet-stream",
            size=result["size"],
            category=result["category"],
        )

        # ----------------------------------------------------
        # 6. Update status
        # ----------------------------------------------------

        repository.update_status(
            document.id,
            "processing",
        )

        # ----------------------------------------------------
        # 7. Ingest
        # ----------------------------------------------------
        print("🔥 DB FILENAME:", document.filename)
        print("🔥 DB STORED NAME:", document.stored_name)
        print("🔥 DOCUMENT ID:", document.id)

        await ingestion_service.ingest(
            file_path=document.path,
            document_id=document.id,
            document_metadata={
                "filename": document.filename,
                "document_id": result["document_id"],
                "category": document.category,
            },
        )

        # ----------------------------------------------------
        # 8. Mark processed
        # ----------------------------------------------------

        repository.update_status(
            document.id,
            "processed",
        )

        db.commit()

        # ----------------------------------------------------
        # 9. Refresh document list
        # ----------------------------------------------------

        return (
            gr.update(
                choices=document_choices(),
                value=None,
            ),
            f"✅ Uploaded: {document.filename}",
        )

    except Exception as e:

        db.rollback()

        return (
            gr.update(
                choices=document_choices(),
                value=None,
            ),
            f"❌ Upload failed: {type(e).__name__}: {e}",
        )

    finally:
        db.close()


# ============================================================
# RAG
# ============================================================

# def ask_question(message, history):

#     if not message:
#         return ""

#     result = rag_service.ask(message)

#     message = {
#         "role": "assistant",
#         "content": result["answer"]
#     }

#     return message

def format_sources(sources):
    if not sources:
        return "No sources found."

    lines = ["### 📚 Sources"]

    for i, source in enumerate(sources, start=1):

        filename = source.get("filename", "Unknown")
        chunk_index = source.get("chunk_index", "N/A")
        score = source.get("score", 0)

        lines.append(
            f"**[{i}] {filename}**  \n"
            f"Chunk: `{chunk_index}`  \n"
            f"Score: `{score:.3f}`"
        )

    return "\n\n".join(lines)

# def ask_question(message, history):

#     if not message.strip():
#         return "Please enter a question."

#     try:

#         result = rag_service.ask(message)

#         return result["answer"]

#     except Exception as e:

#         return f"❌ RAG error: {str(e)}"


def ask_question(message, history):

    if not message.strip():
        return (
            "Please enter a question.",
            "### 📚 Sources\n\nNo sources found.",
        )

    try:

        result = rag_service.ask(
            question=message,
            top_k=5,
        )

        answer = result["answer"]

        sources_text = format_sources(
            result["sources"]
        )

        return (
            answer,
            sources_text,
        )

    except Exception as e:

        return (
            f"❌ RAG error: {str(e)}",
            "### 📚 Sources\n\nNo sources found.",
        )


# ============================================================
# Gradio UI
# ============================================================

with gr.Blocks(title="My RAG") as demo:

    gr.Markdown("# 📚 AI RAG Expert")

    # --------------------------------------------------------
    # Documents
    # --------------------------------------------------------

    with gr.Row():

        with gr.Column(scale=1):

            gr.Markdown("## 📄 Documents")

            documents = gr.Radio(
                choices=document_choices(),
                label="Select a document",
                interactive=True,
            )

            delete_button = gr.Button(
                "🗑️ Delete",
                variant="stop",
            )

            upload = gr.File(
                label="Upload document",
                type="filepath",
            )

            upload_status = gr.Markdown()

        # ----------------------------------------------------
        # Chat
        # ----------------------------------------------------

        # with gr.Column(scale=3):

        #     chatbot = gr.Chatbot(
        #         label="RAG Chat",
        #         height=600
        #     )

        #     message = gr.Textbox(
        #         placeholder="Ask something about your documents...",
        #         label="Question",
        #     )

        #     send = gr.Button(
        #         "Send",
        #         variant="primary",
        #     )
        with gr.Column(scale=3):

            gr.Markdown("### 💬 RAG Chat")

            with gr.Column(scale=1):

                sources = gr.Markdown(
                    "### 📚 Sources\n\n"
                    "Sources will appear here.",
                    render=False,
                )

            with gr.Row():

                with gr.Column(scale=3):

                    chatbot = gr.ChatInterface(
                        fn=ask_question,
                        additional_outputs=[sources],
                    )
                
                with gr.Column(scale=1):
                    sources.render()
                    


    # ========================================================
    # Events
    # ========================================================

    upload.upload(
        fn=upload_document,
        inputs=[upload],
        outputs=[
            documents,
            upload_status,
        ],
    )

    delete_button.click(
        fn=delete_document,
        inputs=[documents],
        outputs=[
            documents,
            upload_status,
        ],
    )


# ============================================================
# Launch
# ============================================================

if __name__ == "__main__":
    demo.launch()