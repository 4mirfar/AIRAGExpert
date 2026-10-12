import json
from pathlib import Path

from app.services.error_analyzer import ErrorAnalyzer


RESULTS_PATH = "evaluation/generation_results.json"


def load_results() -> list[dict]:

    path = Path(RESULTS_PATH)

    if not path.exists():
        raise FileNotFoundError(
            f"Evaluation results not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    if isinstance(data, dict):
        data = data.get("results", [])

    if not isinstance(data, list):
        raise ValueError(
            "Evaluation results must be a list."
        )

    return data


def print_report(report: dict) -> None:

    summary = report["summary"]

    print()
    print("=" * 70)
    print("                    RAG Error Analysis")
    print("=" * 70)

    print(
        f"Total Questions       : "
        f"{summary['total']}"
    )

    print(
        f"Success               : "
        f"{summary['success']}"
    )

    print(
        f"Retrieval Failures    : "
        f"{summary['retrieval_failures']}"
    )

    print(
        f"Retrieval Ranking     : "
        f"{summary['retrieval_ranking']}"
    )

    print(
        f"Generation Failures   : "
        f"{summary['generation_failures']}"
    )

    print(
        f"Faithfulness Failures : "
        f"{summary['faithfulness_failures']}"
    )

    print("=" * 70)

    # ---------------------------------------------------------
    # Detailed failures
    # ---------------------------------------------------------

    print()
    print("                    Failed Questions")
    print("=" * 70)

    for item in report["questions"]:

        if item["category"] == "SUCCESS":
            continue

        print()
        print("-" * 70)

        print(
            f"Question:\n"
            f"{item['question']}"
        )

        print()

        print(
            f"Category:\n"
            f"{item['category']}"
        )

        print()

        print(
            f"Explanation:\n"
            f"{item['explanation']}"
        )

        print()

        print("Expected Answer:")
        print(
            f"  {item.get('expected_answer', 'N/A')}"
        )

        print()

        print("Generated Answer:")
        print(
            f"  {item.get('generated_answer', 'N/A')}"
        )

        print()

        print(
            f"Correct Chunk Rank: "
            f"{item['correct_rank']}"
        )

        print(
            f"Correctness   : "
            f"{item['correctness']:.2f}"
        )

        print(
            f"Relevance     : "
            f"{item['relevance']:.2f}"
        )

        print(
            f"Faithfulness  : "
            f"{item['faithfulness']:.2f}"
        )

        print("-" * 70)


def main():

    print(
        "Loading generation evaluation results..."
    )

    results = load_results()

    analyzer = ErrorAnalyzer()

    report = analyzer.analyze(
        results
    )

    print_report(report)


if __name__ == "__main__":
    main()