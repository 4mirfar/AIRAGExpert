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

    def chat(self, messages: list[dict]) -> str:
        response = self.client.chat(
            model=self.model,
            messages=messages
        )

        return response.message.content.strip()

    # TODO: debug generate stream for ai like generation in ui
    
    # Generate Stream
    # def generate(self, prompt):

    #     stream = self.client.chat(
    #         model=self.model,
    #         messages=[
    #             {
    #                 "role": "user",
    #                 "content": prompt,
    #             }
    #         ],
    #         stream=True,
    #     )

    #     for chunk in stream:
    #         yield chunk["message"]["content"]