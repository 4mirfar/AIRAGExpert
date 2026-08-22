from unittest.mock import Mock

from app.services.llm import LLMService


def test_generate():
    service = LLMService()

    service.client = Mock()

    mock_response = Mock()
    mock_response.response = "FastAPI is a Python web framework."

    service.client.generate.return_value = mock_response

    result = service.generate("What is FastAPI?")

    assert result == "FastAPI is a Python web framework."

    service.client.generate.assert_called_once_with(
        model=service.model,
        prompt="What is FastAPI?",
    )