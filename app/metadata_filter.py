def filter_metadata(
    results,
    category=None,
    technology=None,
    environment=None
):
    """
    Filter candidate documents using metadata.

    Documents with environment='general' are valid
    for all environments.
    """

    filtered = []

    for result in results:

        if (
            category
            and category != "unknown"
            and result.get("category") != category
        ):
            continue

        if (
            technology
            and technology != "unknown"
            and result.get("technology") != technology
        ):
            continue

        if environment:

            result_environment = result.get(
                "environment",
                "general"
            )

            if result_environment not in {
                environment,
                "general"
            }:
                continue

        filtered.append(result)

    return filtered