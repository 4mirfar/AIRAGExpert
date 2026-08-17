# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel

# from app.services.ingestion import IngestionService


# router = APIRouter(
#     prefix="/ingestion",
#     tags=["Ingestion"],
# )

# ingestion_service = IngestionService()


# class IngestionRequest(BaseModel):
#     file_path: str
#     document_id: str
#     metadata: dict = {}


# @router.post("")
# async def ingest_document(request: IngestionRequest):

#     try:

#         chunks = await ingestion_service.ingest(
#             file_path=request.file_path,
#             document_id=request.document_id,
#             document_metadata=request.metadata,
#         )

#         return {
#             "document_id": request.document_id,
#             "status": "processed",
#             "chunk_count": len(chunks),
#             "chunks": [
#                 chunk.model_dump()
#                 for chunk in chunks
#             ],
#         }

#     except FileNotFoundError:

#         raise HTTPException(
#             status_code=404,
#             detail="Document file not found.",
#         )

#     except ValueError as e:

#         raise HTTPException(
#             status_code=400,
#             detail=str(e),
#         )

#     except Exception as e:

#         raise HTTPException(
#             status_code=500,
#             detail=f"Ingestion failed: {str(e)}",
#         )