from pathlib import Path

from pypdf import PdfReader


class PDFParser:
    """
    Production-ready PDF parser.

    Output:
    {
        "text": "...",
        "pages": [
            {
                "page": 1,
                "text": "..."
            }
        ],
        "metadata": {
            "filename": "...",
            "page_count": 10
        }
    }
    """

    async def parse(self, file_path: str) -> dict:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")

        reader = PdfReader(path)

        pages = []
        full_text = []

        for page_number, page in enumerate(reader.pages, start=1):

            text = page.extract_text() or ""

            text = self._clean_text(text)

            pages.append(
                {
                    "page": page_number,
                    "text": text,
                }
            )

            full_text.append(text)

        return {
            "text": "\n".join(full_text),
            "pages": pages,
            "metadata": {
                "filename": path.name,
                "page_count": len(reader.pages),
            },
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Basic text cleaning.
        """

        text = text.replace("\x00", "")
        text = text.replace("\r", "\n")

        lines = [line.strip() for line in text.split("\n")]

        lines = [line for line in lines if line]

        return "\n".join(lines)