from pathlib import Path

from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.parsers.txt_parser import TXTParser

from app.chunking.recursive import RecursiveChunker
from app.chunking.metadata import MetadataBuilder
from app.services.embedding import EmbeddingService
from app.services.qdrant_service import QdrantService

from app.models.chunk import Chunk



class IngestionService:
    """
    Main document ingestion pipeline.

    Flow:

    File
      |
    Parser
      |
    Chunker
      |
    Metadata
      |
    Chunk[]
    """

    def __init__(self):

        self.parsers = {
            ".pdf": PDFParser(),
            ".docx": DOCXParser(),
            ".txt": TXTParser(),
        }

        self.chunker = RecursiveChunker(
            chunk_size=800,
            chunk_overlap=100,
        )

        self.metadata_builder = MetadataBuilder()

        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()
        
        



    async def ingest(
        self,
        file_path: str,
        document_id: str,
        document_metadata: dict,
    ) -> list[Chunk]:


        extension = Path(file_path).suffix.lower()


        # --------------------
        # Select Parser
        # --------------------

        parser = self.parsers.get(extension)

        if not parser:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )


        # --------------------
        # Parse Document
        # --------------------

        parsed_document = await parser.parse(
            file_path
        )


        text = parsed_document["text"]


        if not text.strip():
            raise ValueError(
                "Document contains no readable text"
            )


        # --------------------
        # Chunk Document
        # --------------------

        raw_chunks = self.chunker.split(
            text
        )


        chunks = []


        # --------------------
        # Build Chunk Objects
        # --------------------

        for index, chunk_text in enumerate(raw_chunks):

            print ("Document_Metadata: ", document_metadata)
            print ( "parsed_document[metadata]", parsed_document["metadata"])
            metadata = self.metadata_builder.build(
                document_metadata={
                    **parsed_document["metadata"],
                    **document_metadata,
                },
                chunk_index=index,
            )


            chunk = Chunk(
                chunk_id=metadata["chunk_id"],
                document_id=document_id,
                chunk_index=index,
                text=chunk_text,
                metadata=metadata,
            )


            chunks.append(chunk)

        vectors = self.embedding_service.embed_chunks(chunks)

        self.qdrant_service.create_collection()

        stored_count = self.qdrant_service.upsert_chunks(
            chunks=chunks,
            vectors=vectors,
        )


        return chunks