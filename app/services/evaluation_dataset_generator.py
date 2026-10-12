import json
from pathlib import Path
from typing import Any

from app.services.llm import LLMService
from app.services.qdrant_service import QdrantService


class EvaluationDatasetGenerator:

    def __init__(
        self,
        llm_service: LLMService,
        qdrant_service: QdrantService,
        output_path: str = "evaluation/dataset.json",
    ):
        self.llm_service = llm_service
        self.qdrant_service = qdrant_service
        self.output_path = Path(output_path)

    def generate_for_document(
        self,
        document_id: str,
        num_questions: int = 5,
    ) -> list[dict[str, Any]]:

        # -----------------------------------------
        # 1. Get document chunks
        # -----------------------------------------

        chunks = self.qdrant_service.get_chunks_by_document_id(
            document_id=document_id
        )

        if not chunks:
            raise ValueError(
                f"No chunks found for document: {document_id}"
            )

        dataset = []

        # -----------------------------------------
        # 2. Generate questions from chunks
        # -----------------------------------------

        for chunk in chunks:

            if len(dataset) >= num_questions:
                break

            chunk_id = str(chunk["chunk_id"])
            text = chunk.get("text", "").strip()

            if not text:
                continue

            prompt = self._build_prompt(text)

            response = self.llm_service.generate(prompt)

            generated = self._parse_response(response)

            for item in generated:

                if len(dataset) >= num_questions:
                    break

                dataset.append(
                    {
                        "question": item["question"],
                        "expected_answer": item["expected_answer"],
                        "document_id": str(document_id),
                        "expected_chunk_ids": [chunk_id],
                        "expected_keywords": item["expected_keywords"],
                    }
                )

        return dataset

    def generate_for_documents(
        self,
        document_ids: list[str],
        questions_per_document: int = 5,
    ) -> list[dict[str, Any]]:

        dataset = []

        for document_id in document_ids:

            questions = self.generate_for_document(
                document_id=document_id,
                num_questions=questions_per_document,
            )

            dataset.extend(questions)

        return dataset

    def save_dataset(
        self,
        dataset: list[dict[str, Any]],
    ) -> None:

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.output_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                dataset,
                file,
                indent=2,
                ensure_ascii=False,
            )

    def generate_and_save(
        self,
        document_ids: list[str],
        questions_per_document: int = 5,
    ) -> list[dict[str, Any]]:

        dataset = self.generate_for_documents(
            document_ids=document_ids,
            questions_per_document=questions_per_document,
        )

        self.save_dataset(dataset)

        return dataset
    
    @staticmethod
    def _build_prompt(text: str) -> str:

        return f"""
You are creating an evaluation dataset for a Retrieval-Augmented
Generation system.

Read the following document chunk and generate 2 questions that
can be answered using ONLY the information contained in the chunk.

For each question provide:

- question
- expected_answer
- expected_keywords

The expected_answer must be directly supported by the chunk.

The expected_keywords should contain 3-8 important terms or phrases
from the chunk that are useful for evaluating whether the correct
information was retrieved.

Do not use outside knowledge.

Return ONLY valid JSON in this exact format:

[
  {{
    "question": "...",
    "expected_answer": "...",
    "expected_keywords": ["...", "..."]
  }}
]

DOCUMENT CHUNK:
{text}
"""

    @staticmethod
    def _parse_response(
        response: str,
    ) -> list[dict[str, Any]]:

        try:
            data = json.loads(response)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"LLM returned invalid JSON: {response}"
            ) from exc

        if not isinstance(data, list):
            raise ValueError(
                "LLM response must be a JSON list."
            )

        validated = []

        for item in data:

            if not isinstance(item, dict):
                continue

            question = item.get("question")
            expected_answer = item.get("expected_answer")
            expected_keywords = item.get("expected_keywords")

            if not question or not expected_answer:
                continue

            if not isinstance(expected_keywords, list):
                continue

            expected_keywords = [
                str(keyword).strip()
                for keyword in expected_keywords
                if str(keyword).strip()
            ]

            if not expected_keywords:
                continue

            validated.append(
                {
                    "question": question.strip(),
                    "expected_answer": expected_answer.strip(),
                    "expected_keywords": expected_keywords,
                }
            )

        return validated