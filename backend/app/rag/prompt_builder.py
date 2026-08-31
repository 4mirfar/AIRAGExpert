class PromptBuilder:
    SYSTEM_PROMPT = """
You are a question-answering assistant.

Answer the user's question using ONLY the provided context.

Rules:
1. Do not use outside knowledge.
2. Do not make assumptions.
3. Do not add information that is not explicitly supported by the context.
4. If the context does not contain enough information to answer,
   say that the answer cannot be determined from the provided documents.
5. Keep the answer concise and directly answer the question.

Answer:
"""
    def build(
        self,
        question: str,
        context: str,
    ) -> str:

        return f"""{self.SYSTEM_PROMPT}

Context:
{context}

Question:
{question}

Answer:"""