from query_router import route_query


def main():

    test_cases = [
        {
            "intent": "information"
        },
        {
            "intent": "troubleshooting"
        },
        {
            "intent": "resolution"
        },
        {
            "intent": "unknown"
        }
    ]

    for incident in test_cases:

        result = route_query(
            incident
        )

        print(
            f"\nIntent: "
            f"{incident['intent']}"
        )

        print(
            f"Route: "
            f"{result['route']}"
        )

        print(
            f"Top candidates: "
            f"{result['top_candidates']}"
        )

        print(
            f"Final results: "
            f"{result['final_results']}"
        )


if __name__ == "__main__":
    main()