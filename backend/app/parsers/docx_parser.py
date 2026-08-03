from pathlib import Path

from docx import Document


class DOCXParser:
    """
    Production-ready DOCX parser.

    Output:
    {
        "text": "...",
        "pages": [],
        "metadata": {
            "filename": "...",
            "paragraph_count": 10,
            "table_count": 2
        }
    }
    """

    async def parse(self, file_path: str) -> dict:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")

        document = Document(path)

        paragraphs = []
        full_text = []

        # -------- Paragraphs --------
        for index, paragraph in enumerate(document.paragraphs, start=1):

            text = self._clean_text(paragraph.text)

            if not text:
                continue

            paragraphs.append(
                {
                    "index": index,
                    "text": text,
                    "style": paragraph.style.name,
                }
            )

            full_text.append(text)

        # -------- Tables --------
        tables = []

        for table_index, table in enumerate(document.tables, start=1):

            rows = []

            for row in table.rows:
                rows.append(
                    [
                        self._clean_text(cell.text)
                        for cell in row.cells
                    ]
                )

            tables.append(
                {
                    "index": table_index,
                    "rows": rows,
                }
            )

        return {
            "text": "\n".join(full_text),
            "paragraphs": paragraphs,
            "tables": tables,
            "metadata": {
                "filename": path.name,
                "paragraph_count": len(paragraphs),
                "table_count": len(tables),
                "parser": "python-docx",
            },
        }

    @staticmethod
    def _clean_text(text: str) -> str:

        text = text.replace("\x00", "")
        text = text.replace("\r", "\n")

        lines = [line.strip() for line in text.split("\n")]

        lines = [line for line in lines if line]

        return "\n".join(lines)