from pathlib import Path

from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.parsers.txt_parser import TXTParser

from app.chunking.recursive import RecursiveChunker
from app.chunking.metadata import MetadataBuilder

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

            metadata = self.metadata_builder.build(
                document_metadata={
                    **document_metadata,
                    **parsed_document["metadata"],
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


        return chunks