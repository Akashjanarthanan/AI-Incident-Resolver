from grounding_evaluator import GroundingEvaluator


def main():

    evaluator = GroundingEvaluator()

    claim = (
    "Restart the entire database server."

    )

    evidence = (
        "Run lsnrctl status to verify whether "
        "the Oracle listener is running."
    )

    result = evaluator.evaluate_claim(
        claim,
        evidence
    )

    print("\n" + "=" * 70)
    print("GROUNDING TEST")
    print("=" * 70)

    print("\nClaim:")
    print(result["claim"])

    print(
        f"\nSimilarity: "
        f"{result['similarity']:.4f}"
    )

    print(
        "\nSupported:",
        result["supported"]
    )


if __name__ == "__main__":
    main()