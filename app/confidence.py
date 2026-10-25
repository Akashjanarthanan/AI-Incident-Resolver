def calculate_confidence(results):
    """
    Convert retrieval quality into a simple confidence category.
    """

    if not results:
        return {
            "level": "LOW",
            "score": 0.0,
        }

    best_score = results[0]["reranker_score"]

    if best_score >= 5:
        level = "HIGH"
    elif best_score >= 2:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "level": level,
        "score": float(best_score),
    }