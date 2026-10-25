from query_analyzer import analyze_incident
from query_rewriter import rewrite_query


def process_query(
    original_query,
    conversation_history=None
):
    """
    Analyze the user's query using optional
    conversation context and create a retrieval query.
    """

    incident = analyze_incident(
        original_query,
        conversation_history
    )

    rewritten_query = rewrite_query(
        original_query,
        incident
    )

    return {
        "original_query": original_query,
        "incident": incident,
        "rewritten_query": rewritten_query
    }