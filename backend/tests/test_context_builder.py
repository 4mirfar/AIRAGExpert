from types import SimpleNamespace

from app.retrieval.context_builder import ContextBuilder


def test_build_context_from_results():
    results = [
        SimpleNamespace(
            payload={
                "text": "FastAPI is a modern Python web framework.",
                "filename": "fastapi.pdf",
                "chunk_index": 3,
            }
        ),
        SimpleNamespace(
            payload={
                "text": "FastAPI uses Pydantic for data validation.",
                "filename": "fastapi.pdf",
                "chunk_index": 7,
            }
        ),
    ]

    builder = ContextBuilder()

    context = builder.build(results)

    expected = (
        "[Source 1]\n"
        "File: fastapi.pdf\n"
        "Chunk: 3\n"
        "FastAPI is a modern Python web framework.\n\n"
        "[Source 2]\n"
        "File: fastapi.pdf\n"
        "Chunk: 7\n"
        "FastAPI uses Pydantic for data validation."
    )

    assert context == expected


def test_build_empty_context():
    builder = ContextBuilder()

    context = builder.build([])

    assert context == ""


def test_build_skips_empty_text():
    results = [
        SimpleNamespace(
            payload={
                "text": "",
                "filename": "empty.pdf",
                "chunk_index": 0,
            }
        ),
        SimpleNamespace(
            payload={
                "text": "Useful content.",
                "filename": "document.pdf",
                "chunk_index": 1,
            }
        ),
    ]

    builder = ContextBuilder()

    context = builder.build(results)

    assert "empty.pdf" not in context
    assert "Useful content." in context


def test_build_preserves_result_order():
    results = [
        SimpleNamespace(
            payload={
                "text": "First chunk.",
                "filename": "doc.pdf",
                "chunk_index": 0,
            }
        ),
        SimpleNamespace(
            payload={
                "text": "Second chunk.",
                "filename": "doc.pdf",
                "chunk_index": 1,
            }
        ),
    ]

    builder = ContextBuilder()

    context = builder.build(results)

    assert context.index("First chunk.") < context.index(
        "Second chunk."
    )