from unittest.mock import Mock

from app.retrieval.retriever import Retriever


def test_retrieve_returns_qdrant_results():
    # Arrange
    embedding_service = Mock()
    qdrant_service = Mock()

    question = "What is FastAPI?"
    query_vector = [0.1, 0.2, 0.3]

    expected_results = [
        {
            "score": 0.92,
            "text": "FastAPI is a Python web framework.",
        },
        {
            "score": 0.81,
            "text": "FastAPI is built on Starlette and Pydantic.",
        },
    ]

    embedding_service.embed_text.return_value = query_vector
    qdrant_service.search.return_value = expected_results

    retriever = Retriever(
        embedding_service=embedding_service,
        qdrant_service=qdrant_service,
    )

    # Act
    results = retriever.retrieve(
        question=question,
        top_k=2,
    )

    # Assert
    embedding_service.embed_text.assert_called_once_with(
        question
    )

    qdrant_service.search.assert_called_once_with(
        query_vector=query_vector,
        top_k=2,
    )

    assert results == expected_results



def test_retrieve_uses_default_top_k():
    # Arrange
    embedding_service = Mock()
    qdrant_service = Mock()

    query_vector = [0.1, 0.2, 0.3]

    embedding_service.embed_text.return_value = query_vector
    qdrant_service.search.return_value = []

    retriever = Retriever(
        embedding_service=embedding_service,
        qdrant_service=qdrant_service,
    )

    # Act
    retriever.retrieve(
        "What is FastAPI?"
    )

    # Assert
    qdrant_service.search.assert_called_once_with(
        query_vector=query_vector,
        top_k=5,
    )