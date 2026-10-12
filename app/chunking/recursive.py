from typing import List
# Why is this better than the previous `chunker.py`?

# This implementation:

# ✅ Preserves paragraphs whenever possible.
# ✅ If a paragraph is still too large, it splits it into smaller sections using line breaks.
# ✅ If needed, it further splits by sentences.
# ✅ Then by words.
# ✅ As a last resort, it performs fixed-size character splitting.

# This follows the core idea behind
#  **Recursive Character Text Splitting**, 
# which is widely recommended as the default 
# chunking strategy for RAG systems because 
# it preserves the natural structure and 
# semantic coherence of documents whenever possible. 
# Rather than blindly splitting text at a fixed number of characters, 
# it recursively falls back to smaller text units only when necessary, 
# resulting in higher-quality embeddings and more accurate retrieval. 
# :contentReference[oaicite:0]{index=0}

class RecursiveChunker:
    """
    Recursive text splitter.

    Similar idea to LangChain RecursiveCharacterTextSplitter
    but implemented from scratch.
    """

    DEFAULT_SEPARATORS = [
        "\n\n",
        "\n",
        ". ",
        " ",
        "",
    ]

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        separators: List[str] | None = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or self.DEFAULT_SEPARATORS

    def split(self, text: str) -> List[str]:

        text = text.strip()

        if len(text) <= self.chunk_size:
            return [text]

        return self._split_recursive(
            text,
            self.separators,
        )

    def _split_recursive(
        self,
        text: str,
        separators: List[str],
    ) -> List[str]:

        if len(text) <= self.chunk_size:
            return [text]

        if not separators:
            return self._fixed_split(text)

        separator = separators[0]

        if separator == "":
            return self._fixed_split(text)

        parts = text.split(separator)

        if len(parts) == 1:
            return self._split_recursive(
                text,
                separators[1:],
            )

        chunks = []
        current = ""

        for part in parts:

            candidate = (
                part
                if current == ""
                else current + separator + part
            )

            if len(candidate) <= self.chunk_size:

                current = candidate

            else:

                if current:

                    chunks.extend(
                        self._split_recursive(
                            current,
                            separators[1:],
                        )
                    )

                current = part

        if current:

            chunks.extend(
                self._split_recursive(
                    current,
                    separators[1:],
                )
            )

        return self._apply_overlap(chunks)

    def _fixed_split(
        self,
        text: str,
    ) -> List[str]:

        chunks = []

        step = self.chunk_size - self.chunk_overlap

        start = 0

        while start < len(text):

            end = start + self.chunk_size

            chunks.append(
                text[start:end]
            )

            start += step

        return chunks

    def _apply_overlap(
        self,
        chunks: List[str],
    ) -> List[str]:

        if self.chunk_overlap <= 0:
            return chunks

        merged = []

        previous = ""

        for chunk in chunks:

            if previous:

                overlap = previous[-self.chunk_overlap :]

                merged.append(
                    overlap + chunk
                )

            else:

                merged.append(chunk)

            previous = chunk

        return merged