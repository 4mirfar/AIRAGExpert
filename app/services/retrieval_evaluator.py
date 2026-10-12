from typing import Any


class RetrievalEvaluator:
    """
    Evaluates the quality of the RAG retrieval component.

    For each evaluation sample, we already know which chunk(s)
    contain the ground-truth information.

    The evaluator runs the question through the real Retriever
    and checks whether the expected chunk was retrieved within
    the top K results.

    Example:

        expected_chunk_ids = ["chunk-123"]

        retrieved:
            Top 1 -> chunk-456
            Top 2 -> chunk-123
            Top 3 -> chunk-789

        Recall@1 = 0
        Recall@3 = 1
    """

    def __init__(self, retriever):
        # Use the same Retriever used by the actual RAG pipeline.
        # This ensures that we are evaluating the real retrieval
        # implementation rather than a separate/test implementation.
        self.retriever = retriever

    def evaluate(
        self,
        dataset: list[dict[str, Any]],
        k_values: list[int] | None = None,
    ) -> dict[str, float]:
        """
        Evaluate retrieval performance using Recall@K.

        Args:
            dataset:
                Evaluation samples containing:
                - question
                - expected_chunk_ids

            k_values:
                K values to evaluate.
                Example: [1, 3, 5]

        Returns:
            A dictionary containing Recall@K scores.

            Example:
                {
                    "recall@1": 0.60,
                    "recall@3": 0.85,
                    "recall@5": 0.95,
                }
        """

        # If the caller does not specify K values,
        # evaluate the standard Top-1, Top-3 and Top-5.
        if k_values is None:
            k_values = [1, 3, 5]

        if not dataset:
            raise ValueError("Evaluation dataset is empty.")

        # Initialize counters for each Recall@K metric.
        #
        # We initially store the number of successful retrievals.
        # At the end, we divide by the total number of questions
        # to convert these counts into percentages/proportions.
        results = {
            f"recall@{k}": 0.0
            for k in k_values
        }

        # Evaluate every question in the dataset independently.
        for sample in dataset:

            question = sample["question"]

            # These are the chunk IDs that we know contain
            # the correct information for this question.
            #
            # We use a set so that checking whether a retrieved
            # chunk is a ground-truth chunk is fast and simple.
            expected_chunk_ids = {
                str(chunk_id)
                for chunk_id in sample["expected_chunk_ids"]
            }

            # We only need to retrieve up to the largest K.
            #
            # For [1, 3, 5], retrieving the top 5 results is enough
            # to calculate Recall@1, Recall@3 and Recall@5.
            max_k = max(k_values)

            # Run the question through the actual Retriever.
            #
            # IMPORTANT:
            # Your Retriever uses `question`, not `query`.
            retrieved = self.retriever.retrieve(
                question=question,
                top_k=max_k,
            )

            # Extract the Qdrant point ID from every retrieved result.
            #
            # Your Retriever returns Qdrant ScoredPoint objects,
            # which expose the vector/chunk ID through `result.id`.
            retrieved_ids = [
                str(self._get_chunk_id(result))
                for result in retrieved
            ]

            # Calculate each requested Recall@K.
            for k in k_values:

                # Only consider the first K retrieved chunks.
                top_k_ids = set(
                    retrieved_ids[:k]
                )

                # If at least one expected chunk exists
                # inside the Top-K results, this question
                # counts as a successful retrieval.
                #
                # Example:
                #
                # expected = {"chunk-123"}
                # retrieved = {"chunk-456", "chunk-123", "chunk-789"}
                #
                # intersection != empty -> HIT
                hit = bool(
                    top_k_ids & expected_chunk_ids
                )

                if hit:
                    results[f"recall@{k}"] += 1

        # Convert the number of successful questions into
        # Recall@K proportions.
        #
        # Example:
        # 8 successful questions out of 10
        # -> Recall@K = 0.8 = 80%
        total = len(dataset)

        for key in results:
            results[key] /= total

        return results

    @staticmethod
    def _get_chunk_id(result):
        """
        Extract the chunk ID from a retrieval result.

        The current implementation uses Qdrant ScoredPoint objects,
        where the ID is available as `result.id`.

        Dictionary support is also included so the evaluator can
        work with a Retriever that returns dictionaries in the future.
        """

        # Qdrant ScoredPoint
        if hasattr(result, "id"):
            return result.id

        # Support dictionary-based retrieval results.
        if isinstance(result, dict):

            if "id" in result:
                return result["id"]

            if "chunk_id" in result:
                return result["chunk_id"]

        # If we reach this point, the retrieval result has an
        # unexpected structure and evaluation cannot continue safely.
        raise ValueError(
            f"Cannot extract chunk ID from result: {result}"
        )