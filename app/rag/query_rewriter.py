from app.services.llm import LLMService


class QueryRewriter:

    def __init__(self, llm_service=None):
        self.llm_service = llm_service or LLMService()

    def rewrite(
        self,
        question: str,
        history: list | None = None,
    ) -> str:

        # No history means the question is already standalone.
        if not history:
            return question

        history_text = self._format_history(history)

        prompt = f"""
        You are a component inside a Retrieval-Augmented Generation (RAG)
system.

Your job is to understand the user's latest question and, when
necessary, rewrite it so that it is clear and understandable
without the previous conversation.

The result will be sent directly to a document retrieval system.

IMPORTANT:

- Your response must be ONLY the rewritten question.
- Write normal human language.
- NEVER write Python code.
- NEVER write JavaScript or any other programming code.
- NEVER write a function.
- NEVER write explanations.
- NEVER write instructions.
- NEVER write Markdown.
- NEVER write JSON.
- NEVER include labels such as "Question:", "Answer:", or
  "Search query:".
- NEVER invent information.
- NEVER invent names, people, companies, products, or other entities.
- Only use information explicitly provided in the conversation.
- Resolve words such as "it", "he", "she", "they", "this", and
  "that" only when their meaning is clear from the conversation.
- When the latest question contains a pronoun or reference such as
  "it", "this", "that", "he", "she", or "they", resolve it using the
  most recent relevant topic in the conversation when the reference
  is reasonably clear.

- Prefer the most recent relevant entity or topic over older topics.

- Only leave the reference unchanged when there are multiple equally
  plausible entities or when resolving it would require guessing.
- If the latest question is already clear by itself, return it
  unchanged.
- Preserve the meaning of the user's question.

Example 1:

Conversation:
User: What is DEJEMUL-GATOR?
Assistant: DEJEMUL-GATOR is a demulsifier.

Latest user question:
Who produces it?

Correct response:
Who produces DEJEMUL-GATOR?

Example 2:

Conversation:
User: Who is Amirhossein Farhangian?
Assistant: Amirhossein Farhangian is an AI engineer.

Latest user question:
What has he worked on?

Correct response:
What has Amirhossein Farhangian worked on?

Example 3:

Conversation:
User: What is DEJEMUL-GATOR?
Assistant: DEJEMUL-GATOR is a demulsifier.

Latest user question:
What has he done?

Correct response:
What has he done?

Example 4:

Conversation:
User: What is nonylphenol?

Latest user question:
What are its applications?

Correct response:
What are the applications of nonylphenol?

Example 5:

Conversation:
User: What technologies were used in AI RAG Expert?

Latest user question:
Which database does it use?

Correct response:
Which database does AI RAG Expert use?

Now perform the same task.

Conversation:
{history_text}

Latest user question:
{question}

Your response:
"""

        rewritten = self.llm_service.generate(prompt)
        # print("messages_text", history_text)

        return rewritten.strip()

    @staticmethod
    def _format_history(history: list) -> str:

        messages = []

        for message in history:

            if not isinstance(message, dict):
                continue

            role = message.get("role")
            content = message.get("content")

            if not content:
                continue

            messages.append(
                f"{role}: {content}"
            )

        return "\n".join(messages)