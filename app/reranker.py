from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def rerank(query, results, top_k=3):
    """
    Rerank retrieved documents using a CrossEncoder.

    Args:
        query: User's question.
        results: Candidate documents from hybrid retrieval.
        top_k: Number of final documents to return.

    Returns:
        Reranked results.
    """

    if not results:
        return []

    model = CrossEncoder(MODEL_NAME)

    pairs = [
        (query, result["text"])
        for result in results
    ]

    scores = model.predict(pairs)

    reranked_results = []

    for result, score in zip(results, scores):

        reranked_result = result.copy()
        reranked_result["reranker_score"] = float(score)

        reranked_results.append(reranked_result)

    reranked_results.sort(
        key=lambda item: item["reranker_score"],
        reverse=True
    )

    return reranked_results[:top_k]