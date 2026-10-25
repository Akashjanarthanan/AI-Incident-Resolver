import json
from pathlib import Path

from query_pipeline import process_query
from rag_retriever import retrieve


EVALUATION_FILE = Path(
    "data/evaluation_questions.json"
)


def load_questions():
    with open(
        EVALUATION_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def source_recall(expected_sources, results):

    if not expected_sources:
        return None

    retrieved_sources = {
        result["source"]
        for result in results
    }

    hits = sum(
        source in retrieved_sources
        for source in expected_sources
    )

    return hits / len(expected_sources)


def best_score(results):

    if not results:
        return None

    return results[0]["reranker_score"]


def main():

    questions = load_questions()

    raw_scores = []
    rewritten_scores = []

    raw_recalls = []
    rewritten_recalls = []

    print("\n" + "=" * 80)
    print("RAW QUERY vs REWRITTEN QUERY EVALUATION")
    print("=" * 80)

    for item in questions:

        question = item["question"]

        print("\n" + "-" * 80)
        print(f"{item['id']}: {question}")
        print("-" * 80)

        # ------------------------------------------------
        # RAW QUERY
        # ------------------------------------------------

        raw_results = retrieve(
            question,
            top_candidates=10,
            final_results=3
        )

        raw_score = best_score(
            raw_results
        )

        raw_recall = source_recall(
            item["expected_sources"],
            raw_results
        )

        # ------------------------------------------------
        # QUERY REWRITING
        # ------------------------------------------------

        query_data = process_query(
            question
        )

        rewritten_query = query_data[
            "rewritten_query"
        ]

        rewritten_results = retrieve(
            rewritten_query,
            top_candidates=10,
            final_results=3
        )

        rewritten_score = best_score(
            rewritten_results
        )

        rewritten_recall = source_recall(
            item["expected_sources"],
            rewritten_results
        )

        print("\nRewritten query:")
        print(rewritten_query)

        print(
            f"\nRaw best score: "
            f"{raw_score:.4f}"
            if raw_score is not None
            else "\nRaw best score: N/A"
        )

        print(
            f"Rewritten best score: "
            f"{rewritten_score:.4f}"
            if rewritten_score is not None
            else "Rewritten best score: N/A"
        )

        if (
            raw_score is not None
            and rewritten_score is not None
        ):

            difference = (
                rewritten_score
                - raw_score
            )

            print(
                f"Score difference: "
                f"{difference:+.4f}"
            )

        if raw_recall is not None:

            print(
                f"Raw source recall: "
                f"{raw_recall:.2f}"
            )

            raw_recalls.append(
                raw_recall
            )

        if rewritten_recall is not None:

            print(
                f"Rewritten source recall: "
                f"{rewritten_recall:.2f}"
            )

            rewritten_recalls.append(
                rewritten_recall
            )

        if raw_score is not None:
            raw_scores.append(raw_score)

        if rewritten_score is not None:
            rewritten_scores.append(
                rewritten_score
            )

    # ----------------------------------------------------
    # Overall results
    # ----------------------------------------------------

    print("\n" + "=" * 80)
    print("OVERALL COMPARISON")
    print("=" * 80)

    if raw_scores:

        average_raw_score = (
            sum(raw_scores)
            / len(raw_scores)
        )

        print(
            f"\nAverage raw reranker score: "
            f"{average_raw_score:.4f}"
        )

    if rewritten_scores:

        average_rewritten_score = (
            sum(rewritten_scores)
            / len(rewritten_scores)
        )

        print(
            f"Average rewritten reranker score: "
            f"{average_rewritten_score:.4f}"
        )

    if raw_recalls:

        average_raw_recall = (
            sum(raw_recalls)
            / len(raw_recalls)
        )

        print(
            f"\nAverage raw source recall: "
            f"{average_raw_recall:.2f}"
        )

    if rewritten_recalls:

        average_rewritten_recall = (
            sum(rewritten_recalls)
            / len(rewritten_recalls)
        )

        print(
            f"Average rewritten source recall: "
            f"{average_rewritten_recall:.2f}"
        )


if __name__ == "__main__":
    main()