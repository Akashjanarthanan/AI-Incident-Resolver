import json
import time
from pathlib import Path

from rag_retriever import retrieve


EVALUATION_FILE = Path(
    "data/evaluation_questions.json"
)


def load_evaluation_data():
    with open(
        EVALUATION_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def evaluate_question(item):

    print("\n" + "=" * 70)
    print(f"{item['id']}: {item['question']}")
    print("=" * 70)

    start_time = time.perf_counter()

    results = retrieve(
         item["question"],
         top_candidates=10,
         final_results=3,
    )

    elapsed = time.perf_counter() - start_time

    print(
        f"\nRetrieval latency: "
        f"{elapsed * 1000:.2f} ms"
    )

    retrieved_sources = {
        result["source"]
        for result in results
    }

    # --------------------------------------------------
    # Source evaluation
    # --------------------------------------------------

    expected_sources = set(
        item["expected_sources"]
    )

    if expected_sources:

        source_hits = (
            expected_sources
            .intersection(retrieved_sources)
        )

        source_recall = (
            len(source_hits)
            / len(expected_sources)
        )

    else:

        source_recall = None

    # --------------------------------------------------
    # Keyword evaluation
    # --------------------------------------------------

    expected_keywords = item[
        "expected_keywords"
    ]

    retrieved_text = " ".join(
        result["text"].lower()
        for result in results
    )

    if expected_keywords:

        keyword_hits = sum(
            keyword.lower() in retrieved_text
            for keyword in expected_keywords
        )

        keyword_coverage = (
            keyword_hits
            / len(expected_keywords)
        )

    else:

        keyword_coverage = None

    # --------------------------------------------------
    # Should Answer evaluation
    # --------------------------------------------------

    should_answer = item["should_answer"]

    retrieved_relevant = bool(results)

    if should_answer:

        decision_correct = retrieved_relevant

    else:

        # For an unanswerable question,
        # ideally retrieval should not produce
        # confidently relevant evidence.

        best_score = (
            results[0]["reranker_score"]
            if results
            else None
        )

        decision_correct = (
            best_score is None
            or best_score < 0
        )

    # --------------------------------------------------
    # Display results
    # --------------------------------------------------

    print("\nExpected answer:")
    print(
        "YES"
        if should_answer
        else "NO"
    )

    print("\nRetrieved sources:")

    for result in results:

        print(
            f"- {result['source']} "
            f"(Chunk {result['chunk_id']}) "
            f"Score={result['reranker_score']:.4f}"
        )

    if source_recall is not None:

        print(
            f"\nSource Recall: "
            f"{source_recall:.2f}"
        )

    if keyword_coverage is not None:

        print(
            f"Keyword Coverage: "
            f"{keyword_coverage:.2f}"
        )

    print(
        "\nShould-Answer Decision: "
        f"{'PASS' if decision_correct else 'FAIL'}"
    )

    return {
        "source_recall": source_recall,
        "keyword_coverage": keyword_coverage,
        "decision_correct": decision_correct,
    }


def main():

    evaluation_data = (
        load_evaluation_data()
    )

    results = []

    for item in evaluation_data:

        metrics = evaluate_question(item)

        results.append(metrics)

    # --------------------------------------------------
    # Aggregate metrics
    # --------------------------------------------------

    source_scores = [
        item["source_recall"]
        for item in results
        if item["source_recall"] is not None
    ]

    keyword_scores = [
        item["keyword_coverage"]
        for item in results
        if item["keyword_coverage"] is not None
    ]

    decision_scores = [
        item["decision_correct"]
        for item in results
    ]

    print("\n" + "=" * 70)
    print("OVERALL EVALUATION")
    print("=" * 70)

    if source_scores:

        print(
            "\nAverage Source Recall: "
            f"{sum(source_scores) / len(source_scores):.2f}"
        )

    if keyword_scores:

        print(
            "Average Keyword Coverage: "
            f"{sum(keyword_scores) / len(keyword_scores):.2f}"
        )

    decision_accuracy = (
        sum(decision_scores)
        / len(decision_scores)
    )

    print(
        "Should-Answer Accuracy: "
        f"{decision_accuracy:.2f}"
    )


if __name__ == "__main__":
    main()