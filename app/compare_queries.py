import time

from rag_retriever import retrieve
from query_pipeline import process_query


def run_retrieval(label, query):
    """
    Run retrieval and display the top results.
    """

    print("\n" + "=" * 70)
    print(label)
    print("=" * 70)

    print(f"\nQuery:")
    print(query)

    start_time = time.perf_counter()

    results = retrieve(
        query,
        top_candidates=10,
        final_results=3
    )

    elapsed = time.perf_counter() - start_time

    print(
        f"\nRetrieval latency: "
        f"{elapsed * 1000:.2f} ms"
    )

    if not results:
        print("\nNo results found.")
        return None

    print(
        f"\nBest reranker score: "
        f"{results[0]['reranker_score']:.4f}"
    )

    print("\nRetrieved sources:")

    for rank, result in enumerate(
        results,
        start=1
    ):
        print(
            f"{rank}. "
            f"{result['source']} "
            f"(Chunk {result['chunk_id']}) "
            f"Score={result['reranker_score']:.4f}"
        )

    return results


def main():

    original_query = input(
        "\nEnter your incident:\n> "
    )

    print("\nProcessing query...")

    query_data = process_query(
        original_query
    )

    rewritten_query = query_data[
        "rewritten_query"
    ]

    print("\n" + "=" * 70)
    print("QUERY TRANSFORMATION")
    print("=" * 70)

    print("\nOriginal query:")
    print(original_query)

    print("\nStructured incident:")
    print(query_data["incident"])

    print("\nRewritten query:")
    print(rewritten_query)

    before_results = run_retrieval(
        "BEFORE: RAW QUERY",
        original_query
    )

    after_results = run_retrieval(
        "AFTER: REWRITTEN QUERY",
        rewritten_query
    )

    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)

    if before_results and after_results:

        before_score = (
            before_results[0]["reranker_score"]
        )

        after_score = (
            after_results[0]["reranker_score"]
        )

        print(
            f"\nRaw query score:       "
            f"{before_score:.4f}"
        )

        print(
            f"Rewritten query score: "
            f"{after_score:.4f}"
        )

        difference = after_score - before_score

        print(
            f"Difference:            "
            f"{difference:+.4f}"
        )

        if difference > 0:
            print(
                "\nThe rewritten query produced "
                "a higher reranker score."
            )

        elif difference < 0:
            print(
                "\nThe rewritten query produced "
                "a lower reranker score."
            )

        else:
            print(
                "\nBoth queries produced "
                "the same score."
            )


if __name__ == "__main__":
    main()