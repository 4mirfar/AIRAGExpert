from app.rag.prompt_builder import PromptBuilder


def test_build_prompt():
    builder = PromptBuilder()

    question = "What is FastAPI?"

    context = (
        "[Source 1]\n"
        "File: fastapi.pdf\n"
        "FastAPI is a Python web framework."
    )

    prompt = builder.build(
        question=question,
        context=context,
    )

    assert "What is FastAPI?" in prompt
    assert "FastAPI is a Python web framework." in prompt
    assert "Context:" in prompt
    assert "Question:" in prompt
    assert "Answer:" in prompt


def test_prompt_contains_system_instructions():
    builder = PromptBuilder()

    prompt = builder.build(
        question="What is FastAPI?",
        context="FastAPI is a Python framework.",
    )

    assert "using only the provided context" in prompt
    assert "Do not invent facts" in prompt


def test_prompt_handles_empty_context():
    builder = PromptBuilder()

    prompt = builder.build(
        question="What is FastAPI?",
        context="",
    )

    assert "What is FastAPI?" in prompt
    assert "Context:" in prompt
    assert "Answer:" in prompt