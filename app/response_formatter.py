def get_source(source_id, retrieved_context):
    """
    Resolve a source ID to the actual retrieved chunk.
    """

    if not isinstance(source_id, int):
        return "Unknown source"

    if source_id < 0 or source_id >= len(retrieved_context):
        return "Unknown source"

    item = retrieved_context[source_id]

    return (
        f"{item['source']} "
        f"(Chunk {item['chunk_id']})"
    )


def format_response(answer, retrieved_context):

    print("\n" + "=" * 70)
    print("AI INCIDENT RESOLVER")
    print("=" * 70)

    print("\nINCIDENT SUMMARY")
    print(answer["incident_summary"])

    print("\nLIKELY CAUSE")
    print(answer["likely_cause"])

    print("\nCONFIDENCE")
    print(answer["confidence"])

    print("\nEVIDENCE")

    for item in answer["evidence"]:

        source = get_source(
            item["source_id"],
            retrieved_context
        )

        print(f"\n- {item['statement']}")
        print(f"  Source: {source}")

    print("\nRECOMMENDED INVESTIGATION")

    for index, item in enumerate(
        answer["investigation_steps"],
        start=1
    ):

        source = get_source(
            item["source_id"],
            retrieved_context
        )

        print(f"\n{index}. {item['step']}")
        print(f"   Source: {source}")

    print("\nRECOMMENDED RESOLUTION")

    for item in answer["recommended_resolution"]:

        source = get_source(
            item["source_id"],
            retrieved_context
        )

        print(f"\n- {item['action']}")
        print(f"  Source: {source}")

    print("\nWARNINGS")

    if answer["warnings"]:

        for warning in answer["warnings"]:
            print(f"- {warning}")

    else:
        print("None")