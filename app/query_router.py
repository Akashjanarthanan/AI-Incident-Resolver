def route_query(incident):
    """
    Decide the retrieval strategy based on the
    structured incident intent.
    """

    intent = incident.get(
        "intent",
        "unknown"
    )

    if intent == "information":

        return {
            "route": "direct_lookup",
            "top_candidates": 5,
            "final_results": 2
        }

    if intent == "troubleshooting":

        return {
            "route": "troubleshooting",
            "top_candidates": 10,
            "final_results": 3
        }

    if intent == "resolution":

        return {
            "route": "resolution",
            "top_candidates": 10,
            "final_results": 5
        }

    return {
        "route": "general",
        "top_candidates": 10,
        "final_results": 3
    }