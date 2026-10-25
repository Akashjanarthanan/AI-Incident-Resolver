from retrieval_engine import RetrievalEngine


engine = RetrievalEngine()


def retrieve(
    query,
    incident=None,
    top_candidates=10,
    final_results=3
):
    """
    Retrieve using the search query and
    structured incident metadata.
    """

    category = None
    technology = None
    environment = None

    if incident:

        category = incident.get(
            "category"
        )

        technology = incident.get(
            "technology"
        )

        environment = incident.get(
            "environment"
        )

    return engine.retrieve(
        query,
        category=category,
        technology=technology,
        environment=environment,
        top_candidates=top_candidates,
        final_results=final_results
    )