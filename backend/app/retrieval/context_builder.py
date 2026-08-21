class ContextBuilder:
    """
    Builds a context string from retrieved chunks.

    The context is later passed to the LLM as part of the prompt.
    """

    def build(self, results) -> str:
        if not results:
            return ""

        context_parts = []

        for index, result in enumerate(results, start=1):
            payload = result.payload

            text = payload.get("text", "").strip()

            if not text:
                continue

            filename = payload.get("filename", "Unknown source")
            chunk_index = payload.get("chunk_index", "Unknown")

            context_parts.append(
                f"[Source {index}]\n"
                f"File: {filename}\n"
                f"Chunk: {chunk_index}\n"
                f"{text}"
            )

        return "\n\n".join(context_parts)