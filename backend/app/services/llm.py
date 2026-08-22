from ollama import Client


class LLMService:
    def __init__(
        self,
        model: str = "llama3.2:3b",
        host: str = "http://localhost:11434",
    ):
        self.model = model

        self.client = Client(
            host=host,
        )

    def generate(self, prompt: str) -> str:
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
        )

        return response.response.strip()