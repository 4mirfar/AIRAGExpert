import json
from typing import Any

from app.services.llm import LLMService


class AnswerEvaluator:

    """
    Uses an LLM to evaluate the quality of a generated RAG answer.

    We evaluate three things:

    1. Correctness
       Is the generated answer consistent with the expected answer?

    2. Relevance
       Does the generated answer actually answer the question?

    3. Faithfulness
       Is the generated answer supported by the retrieved context?
    """

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm_service = llm_service

    def evaluate(
        self,
        question: str,
        expected_answer: str,
        generated_answer: str,
        context: str,
    ) -> dict[str, Any]:

        prompt = self._build_prompt(
            question=question,
            expected_answer=expected_answer,
            generated_answer=generated_answer,
            context=context,
        )

        response = self.llm_service.generate(prompt)

        return self._parse_response(response)

    @staticmethod
    def _build_prompt(
        question: str,
        expected_answer: str,
        generated_answer: str,
        context: str,
    ) -> str:

        return f"""
You are an evaluator for a Retrieval-Augmented Generation (RAG) system.

Evaluate the generated answer using ONLY the information provided below.

QUESTION:
{question}

EXPECTED ANSWER:
{expected_answer}

GENERATED ANSWER:
{generated_answer}

RETRIEVED CONTEXT:
{context}

Evaluate three dimensions.

1. CORRECTNESS

Does the generated answer provide the same essential information
as the expected answer?

Score:
0.0 = completely incorrect
0.5 = partially correct
1.0 = fully correct

2. RELEVANCE

Does the generated answer directly answer the question?

Score:
0.0 = irrelevant
0.5 = partially relevant
1.0 = directly answers the question

3. FAITHFULNESS

Is the generated answer supported by the retrieved context?

Score:
0.0 = unsupported or contradicts the context
0.5 = partially supported
1.0 = fully supported

Return ONLY valid JSON.

Use exactly this format:

{{
    "correctness": 0.0,
    "relevance": 0.0,
    "faithfulness": 0.0,
    "reason": "short explanation"
}}
"""

    @staticmethod
    def _parse_response(
        response: str,
    ) -> dict[str, Any]:

        try:
            data = json.loads(response)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"LLM judge returned invalid JSON:\n{response}"
            ) from exc

        required_fields = [
            "correctness",
            "relevance",
            "faithfulness",
            "reason",
        ]

        for field in required_fields:

            if field not in data:
                raise ValueError(
                    f"Missing field '{field}' "
                    f"in answer evaluator response: {data}"
                )

        # -----------------------------------------------------
        # Validate scores
        # -----------------------------------------------------

        for field in [
            "correctness",
            "relevance",
            "faithfulness",
        ]:

            score = data[field]

            if not isinstance(
                score,
                (int, float),
            ):
                raise ValueError(
                    f"{field} must be a number."
                )

            if not 0.0 <= float(score) <= 1.0:
                raise ValueError(
                    f"{field} must be between 0 and 1."
                )

            data[field] = float(score)

        data["reason"] = str(
            data["reason"]
        ).strip()

        return data