from query_analyzer import analyze_incident
from query_rewriter import rewrite_query


def main():

    original_query = (
        "db down after prod deploy pls check ora 12541"
    )

    incident = analyze_incident(
        original_query
    )

    rewritten = rewrite_query(
        original_query,
        incident
    )

    print("\nOriginal Query:")
    print(original_query)

    print("\nStructured Incident:")
    print(incident)

    print("\nRewritten Query:")
    print(rewritten)


if __name__ == "__main__":
    main()