import gradio as gr
from pathlib import Path
import uuid

from app.services.rag import RAGService
from app.services.embedding import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.storage import StorageService
from app.services.validation import FileValidationService
from app.services.ingestion import IngestionService

from app.database.database import SessionLocal
from app.repositories.document_repository import DocumentRepository


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
# Upload + Ingestion
# ============================================================

async def process_file(file):

    if not file:
        return "❌ Please upload a file."

    db = SessionLocal()

    try:
        file_path = Path(str(file))
        filename = file_path.name

        repository = DocumentRepository(db)

        document_id = str(uuid.uuid4())

        document = repository.create(
            document_id=document_id,
            filename=filename,
            stored_name=filename,
            path=str(file_path),
            extension=file_path.suffix.lower(),
            mime_type="application/octet-stream",
            size=file_path.stat().st_size,
            category="documents",
        )

        repository.update_status(
            document.id,
            "processing",
        )

        try:

            chunks = await ingestion_service.ingest(
                file_path=str(file_path),
                document_id=document.id,
                document_metadata={
                    "filename": filename,
                    "category": "documents",
                },
            )

            repository.update_status(
                document.id,
                "processed",
            )

        except Exception:

            repository.update_status(
                document.id,
                "failed",
            )

            raise

        return (
            f"✅ **{filename}** processed successfully.\n\n"
            f"Chunks: **{len(chunks)}**"
        )

    except Exception as e:

        return f"❌ Error: {type(e).__name__}: {e}"

    finally:
        db.close()

# ============================================================
# RAG Question
# ============================================================

def ask_question(message, history):

    if not message.strip():
        return "Please enter a question."

    try:

        result = rag_service.ask(message)

        return result["answer"]

    except Exception as e:

        return f"❌ RAG error: {str(e)}"


# ============================================================
# Gradio UI
# ============================================================

with gr.Blocks(title="AI RAG Expert") as demo:

    gr.Markdown(
        """
        # 📚 AI RAG Expert

        Upload a document and ask questions about it.
        """
    )

    # --------------------------------------------------------
    # Upload section
    # --------------------------------------------------------

    with gr.Row():

        file_input = gr.File(
            label="Upload Document",
            file_types=[".pdf", ".docx", ".txt"],
            type="filepath",
        )

        process_button = gr.Button(
            "Process Document",
            variant="primary",
        )

    upload_status = gr.Markdown(
        value="No document uploaded."
    )

    process_button.click(
        fn=process_file,
        inputs=file_input,
        outputs=upload_status,
    )

    gr.Markdown("---")

    # --------------------------------------------------------
    # Chat section
    # --------------------------------------------------------

    chatbot = gr.ChatInterface(
        fn=ask_question,
        title="Ask Questions",
        description=(
            "Ask questions about your uploaded documents."
        ),
    )


# ============================================================
# Start
# ============================================================

if __name__ == "__main__":
    demo.launch()