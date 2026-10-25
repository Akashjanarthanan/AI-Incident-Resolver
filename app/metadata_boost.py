def apply_metadata_boost(
    results,
    category=None,
    technology=None,
    boost=0.50
):
    """
    Add a small ranking boost when retrieved chunks
    match the detected incident metadata.

    The original retrieval score is preserved.
    """

    boosted_results = []

    for result in results:

        metadata_score = 0.0

        if (
            category
            and category != "unknown"
            and result.get("category")
            == category
        ):
            metadata_score += boost

        if (
            technology
            and technology != "unknown"
            and result.get("technology")
            == technology
        ):
            metadata_score += boost

        updated_result = result.copy()

        updated_result["metadata_boost"] = (
            metadata_score
        )

        updated_result["combined_score"] = (
            result.get("reranker_score", 0.0)
            + metadata_score
        )

        boosted_results.append(
            updated_result
        )

    boosted_results.sort(
        key=lambda item:
        item["combined_score"],
        reverse=True
    )

    return boosted_results