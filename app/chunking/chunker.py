from uuid import uuid4

# why did you choose these numbers for this chunker and what makes you chage it?
# find and search for multiple chunkers

class Chunker:
    """
    Simple recursive-friendly chunker.

    Input:
    {
        "text": "...",
        "metadata": {...}
    }

    Output:
    [
        {
            "chunk_id": "...",
            "chunk_index": 0,
            "text": "...",
            "metadata": {...}
        }
    ]
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, document: dict) -> list[dict]:

        text = document["text"]
        metadata = document["metadata"]

        chunks = []

        start = 0
        chunk_index = 0

        while start < len(text):

            end = start + self.chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:

                chunks.append(
                    {
                        "chunk_id": str(uuid4()),
                        "chunk_index": chunk_index,
                        "text": chunk_text,
                        "metadata": metadata.copy(),
                    }
                )

                chunk_index += 1

            start += self.chunk_size - self.chunk_overlap

        return chunks