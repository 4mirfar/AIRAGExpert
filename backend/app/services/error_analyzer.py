from typing import Any


class ErrorAnalyzer:

    """
    Analyzes RAG evaluation results and classifies failures.

    The goal is not to change the RAG system here.
    The goal is to understand WHY a question failed.

    Failure categories:

    1. RETRIEVAL_FAILURE
       The expected chunk was not retrieved.

    2. RETRIEVAL_RANKING
       The expected chunk was retrieved, but ranked too low.

    3. GENERATION_FAILURE
       The correct information was retrieved, but the generated
       answer was incorrect or incomplete.

    4. FAITHFULNESS_FAILURE
       The answer contains information that is not supported
       by the retrieved context.

    5. SUCCESS
       Retrieval and generation both performed well.
    """

    def analyze(
        self,
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:

        analysis = []

        for result in results:

            correct_rank = result.get(
                "correct_rank"
            )

            recall_at_5 = (
                correct_rank is not None
                and correct_rank <= 5
            )

            correctness = result.get(
                "correctness",
                0.0,
            )

            relevance = result.get(
                "relevance",
                0.0,
            )

            faithfulness = result.get(
                "faithfulness",
                0.0,
            )

            # -------------------------------------------------
            # Classify the failure
            # -------------------------------------------------

            if not recall_at_5:

                category = "RETRIEVAL_FAILURE"

                explanation = (
                    "The expected chunk was not "
                    "retrieved within top-5."
                )

            elif correct_rank > 1 and (
                correctness < 0.8
                or relevance < 0.8
            ):

                category = "GENERATION_FAILURE"

                explanation = (
                    "The correct chunk was retrieved, "
                    "but the generated answer was "
                    "incorrect or insufficient."
                )

            elif faithfulness < 0.8:

                category = "FAITHFULNESS_FAILURE"

                explanation = (
                    "The answer is not sufficiently "
                    "supported by the retrieved context."
                )

            elif correct_rank > 1:

                category = "RETRIEVAL_RANKING"

                explanation = (
                    "The correct chunk was retrieved "
                    "but was not ranked first."
                )

            else:

                category = "SUCCESS"

                explanation = (
                    "Retrieval and generation performed "
                    "successfully."
                )

            analysis.append(
                {
                    "question": result["question"],

                    "expected_answer": result.get(
                        "expected_answer"
                    ),

                    "generated_answer": result.get(
                        "generated_answer"
                    ),

                    "category": category,

                    "explanation": explanation,

                    "correct_rank": correct_rank,

                    "correctness": correctness,

                    "relevance": relevance,

                    "faithfulness": faithfulness,
                }
            )

        return self._build_summary(
            analysis
        )

    @staticmethod
    def _build_summary(
        analysis: list[dict[str, Any]],
    ) -> dict[str, Any]:

        summary = {
            "total": len(analysis),
            "success": 0,
            "retrieval_failures": 0,
            "retrieval_ranking": 0,
            "generation_failures": 0,
            "faithfulness_failures": 0,
        }

        for item in analysis:

            category = item["category"]

            if category == "SUCCESS":
                summary["success"] += 1

            elif category == "RETRIEVAL_FAILURE":
                summary["retrieval_failures"] += 1

            elif category == "RETRIEVAL_RANKING":
                summary["retrieval_ranking"] += 1

            elif category == "GENERATION_FAILURE":
                summary["generation_failures"] += 1

            elif category == "FAITHFULNESS_FAILURE":
                summary["faithfulness_failures"] += 1

        return {
            "summary": summary,
            "questions": analysis,
        }
