import json

from grounding_evaluator import GroundingEvaluator
from llm import generate_answer
from query_pipeline import process_query
from rag_retriever import retrieve


def normalize_claim(claim):
    """
    Normalize claim text so duplicate claims can be detected.
    """

    return " ".join(
        claim.lower().split()
    )


def collect_claims(answer):
    """
    Collect evidence, investigation, and resolution claims.
    Remove exact duplicates.
    """

    claims = []

    for item in answer.get(
        "evidence",
        []
    ):

        claims.append(
            {
                "type": "evidence",
                "claim": item.get(
                    "statement",
                    ""
                ),
                "source_id": item.get(
                    "source_id"
                )
            }
        )

    for item in answer.get(
        "investigation_steps",
        []
    ):

        claims.append(
            {
                "type": "investigation",
                "claim": item.get(
                    "step",
                    ""
                ),
                "source_id": item.get(
                    "source_id"
                )
            }
        )

    for item in answer.get(
        "recommended_resolution",
        []
    ):

        claims.append(
            {
                "type": "resolution",
                "claim": item.get(
                    "action",
                    ""
                ),
                "source_id": item.get(
                    "source_id"
                )
            }
        )

    unique_claims = []
    seen = set()

    for item in claims:

        claim = item["claim"].strip()

        if not claim:
            continue

        normalized = normalize_claim(
            claim
        )

        if normalized in seen:
            continue

        seen.add(normalized)

        unique_claims.append(item)

    return unique_claims


def main():

    query = input(
        "\nEnter an incident:\n> "
    )

    print("\nProcessing incident...")

    query_data = process_query(
        query
    )

    rewritten_query = query_data[
        "rewritten_query"
    ]

    print(
        f"\nRewritten query:\n"
        f"{rewritten_query}"
    )

    print("\nRetrieving evidence...")

    retrieved_context = retrieve(
        rewritten_query,
        top_candidates=10,
        final_results=3
    )

    if not retrieved_context:

        print(
            "\nNo evidence retrieved."
        )

        return

    print("\nGenerating answer...")

    answer = generate_answer(
        query,
        retrieved_context
    )

    print("\nGenerated Answer:")
    print(
        json.dumps(
            answer,
            indent=4
        )
    )

    evaluator = GroundingEvaluator()

    claims = collect_claims(
        answer
    )

    print(
        f"\nUnique claims evaluated: "
        f"{len(claims)}"
    )

    print("\n" + "=" * 70)
    print("GROUNDING EVALUATION")
    print("=" * 70)

    supported_count = 0

    for index, item in enumerate(
        claims,
        start=1
    ):

        claim = item["claim"]
        source_id = item["source_id"]

        print(
            f"\nClaim {index} "
            f"({item['type']}):"
        )

        print(claim)

        if (
            not isinstance(source_id, int)
            or source_id < 0
            or source_id >= len(retrieved_context)
        ):

            print(
                "\nSource: INVALID"
            )

            print(
                "Similarity: 0.0000"
            )

            print(
                "Status: UNSUPPORTED"
            )

            continue

        evidence = retrieved_context[
            source_id
        ]["text"]

        result = evaluator.evaluate_claim(
            claim,
            evidence
        )

        if result["supported"]:
            supported_count += 1

        print(
            f"\nSource: "
            f"{retrieved_context[source_id]['source']}"
            f" "
            f"(Chunk "
            f"{retrieved_context[source_id]['chunk_id']}"
            f")"
        )

        print(
            f"Similarity: "
            f"{result['similarity']:.4f}"
        )

        print(
            "Status: "
            + (
                "SUPPORTED"
                if result["supported"]
                else "UNSUPPORTED"
            )
        )

        print("\nEvidence used:")

        print(
            evidence[:500]
        )

    if claims:

        grounding_score = (
            supported_count
            / len(claims)
        )

        print(
            "\n" + "=" * 70
        )

        print(
            f"Unique-claim grounding score: "
            f"{grounding_score:.2f}"
        )

    else:

        print(
            "\nNo claims were generated."
        )


if __name__ == "__main__":
    main()