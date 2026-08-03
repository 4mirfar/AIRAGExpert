from pathlib import Path


class TXTParser:
    """
    Production-ready TXT parser.

    Output:
    {
        "text": "...",
        "lines": [
            {
                "line": 1,
                "text": "..."
            }
        ],
        "metadata": {
            "filename": "...",
            "line_count": 120,
            "character_count": 5321,
            "parser": "txt"
        }
    }
    """

    async def parse(self, file_path: str) -> dict:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")

        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        text = self._clean_text(text)

        lines = []

        for index, line in enumerate(text.splitlines(), start=1):

            if not line.strip():
                continue

            lines.append(
                {
                    "line": index,
                    "text": line.strip(),
                }
            )

        return {
            "text": text,
            "lines": lines,
            "metadata": {
                "filename": path.name,
                "line_count": len(lines),
                "character_count": len(text),
                "parser": "txt",
            },
        }

    @staticmethod
    def _clean_text(text: str) -> str:

        text = text.replace("\x00", "")
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        lines = [line.strip() for line in text.split("\n")]

        lines = [line for line in lines if line]

        return "\n".join(lines)