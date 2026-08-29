from typing import Any

from app.services.rag import RAGService
from app.services.answer_evaluator import AnswerEvaluator


class GenerationEvaluator:

    def __init__(
        self,
        rag_service: RAGService,
        answer_evaluator: AnswerEvaluator,
    ):
        self.rag_service = rag_service
        self.answer_evaluator = answer_evaluator

    def evaluate(
        self,
        dataset: list[dict[str, Any]],
    ) -> dict[str, Any]:

        if not dataset:
            raise ValueError(
                "Evaluation dataset is empty."
            )

        results = []

        total_keyword_coverage = 0.0
        total_correctness = 0.0
        total_relevance = 0.0
        total_faithfulness = 0.0

        # -----------------------------------------------------
        # Evaluate every question
        # -----------------------------------------------------

        for sample in dataset:

            question = sample["question"]

            expected_answer = sample[
                "expected_answer"
            ]

            expected_keywords = sample.get(
                "expected_keywords",
                [],
            )

            # -------------------------------------------------
            # Run the real RAG pipeline
            # -------------------------------------------------

            rag_result = self.rag_service.ask(
                question=question,
                top_k=5,
            )

            retrieved_sources = rag_result["sources"]

            correct_rank = self._get_correct_rank(
                retrieved_sources=retrieved_sources,
                expected_chunk_ids=sample[
                    "expected_chunk_ids"
                ],
            )

            generated_answer = rag_result[
                "answer"
            ]

            context = rag_result.get(
                "context",
                "",
            )

            # -------------------------------------------------
            # Keyword evaluation
            # -------------------------------------------------

            keyword_result = (
                self._evaluate_keywords(
                    answer=generated_answer,
                    expected_keywords=expected_keywords,
                )
            )

            keyword_coverage = (
                keyword_result["coverage"]
            )

            # -------------------------------------------------
            # LLM-as-a-Judge evaluation
            # -------------------------------------------------

            judge_result = (
                self.answer_evaluator.evaluate(
                    question=question,
                    expected_answer=expected_answer,
                    generated_answer=generated_answer,
                    context=context,
                )
            )

            # -------------------------------------------------
            # Accumulate scores
            # -------------------------------------------------

            total_keyword_coverage += (
                keyword_coverage
            )

            total_correctness += (
                judge_result["correctness"]
            )

            total_relevance += (
                judge_result["relevance"]
            )

            total_faithfulness += (
                judge_result["faithfulness"]
            )

            # -------------------------------------------------
            # Store detailed result
            # -------------------------------------------------

            results.append(
                {
                    "question": question,
                    "expected_answer": expected_answer,
                    "generated_answer": generated_answer,

                    "expected_keywords":
                        expected_keywords,

                    "matched_keywords":
                        keyword_result[
                            "matched_keywords"
                        ],

                    "missing_keywords":
                        keyword_result[
                            "missing_keywords"
                        ],

                    "keyword_coverage":
                        keyword_coverage,


                    "correct_rank":
                        correct_rank,

                    "correctness":
                        judge_result[
                            "correctness"
                        ],

                    "relevance":
                        judge_result[
                            "relevance"
                        ],

                    "faithfulness":
                        judge_result[
                            "faithfulness"
                        ],

                    "reason":
                        judge_result["reason"],

                    "sources":
                        rag_result.get(
                            "sources",
                            [],
                        ),
                }
            )

        # -----------------------------------------------------
        # Calculate averages
        # -----------------------------------------------------

        total = len(dataset)

        return {
            "total_questions": total,

            "keyword_coverage":
                total_keyword_coverage / total,

            "correctness":
                total_correctness / total,

            "relevance":
                total_relevance / total,

            "faithfulness":
                total_faithfulness / total,

            "results": results,
        }

    @staticmethod
    def _evaluate_keywords(
        answer: str,
        expected_keywords: list[str],
    ) -> dict[str, Any]:

        if not expected_keywords:
            return {
                "coverage": 0.0,
                "matched_keywords": [],
                "missing_keywords": [],
            }

        answer_lower = answer.lower()

        matched_keywords = []
        missing_keywords = []

        for keyword in expected_keywords:

            keyword_lower = (
                keyword.lower().strip()
            )

            if not keyword_lower:
                continue

            if keyword_lower in answer_lower:
                matched_keywords.append(
                    keyword
                )
            else:
                missing_keywords.append(
                    keyword
                )

        total_keywords = (
            len(matched_keywords)
            + len(missing_keywords)
        )

        coverage = (
            len(matched_keywords)
            / total_keywords
            if total_keywords
            else 0.0
        )

        return {
            "coverage": coverage,
            "matched_keywords":
                matched_keywords,
            "missing_keywords":
                missing_keywords,
        }


    def _get_correct_rank(
        self,
        retrieved_sources,
        expected_chunk_ids,
    ):
        """
        Find the position of the expected chunk
        in the retrieved results.

        Returns:
            1, 2, 3, ...
            None if the expected chunk was not retrieved.
        """

        expected_chunk_ids = {
            str(chunk_id)
            for chunk_id in expected_chunk_ids
        }

        for rank, source in enumerate(
            retrieved_sources,
            start=1,
        ):

            # RAGService already gives us the chunk_id.
            chunk_id = str(
                source["chunk_id"]
            )

            if chunk_id in expected_chunk_ids:
                return rank

        return None