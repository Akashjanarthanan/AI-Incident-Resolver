import json
from pathlib import Path

from llm import generate_answer
from query_pipeline import process_query
from rag_retriever import retrieve


EVALUATION_FILE = Path(
    "data/evaluation_questions.json"
)


def load_questions():
    with open(
        EVALUATION_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def check_answer_points(answer_text, expected_points):
    """
    Simple baseline answer coverage check.

    This is a lexical diagnostic, not a full semantic
    evaluation.
    """

    answer_lower = answer_text.lower()

    if not expected_points:
        return None

    matches = []

    for point in expected_points:

        if point.lower() in answer_lower:
            matches.append(point)

    return len(matches) / len(expected_points)


def validate_citations(answer, retrieved_context):
    """
    Verify that source IDs referenced by the LLM
    actually exist in the retrieved context.
    """

    valid_ids = set(
        range(len(retrieved_context))
    )

    invalid_ids = []

    sections = [
        answer.get("evidence", []),
        answer.get("investigation_steps", []),
        answer.get("recommended_resolution", [])
    ]

    for section in sections:

        for item in section:

            source_id = item.get("source_id")

            if source_id not in valid_ids:
                invalid_ids.append(source_id)

    total_items = sum(
        len(section)
        for section in sections
    )

    if total_items == 0:
        return 1.0

    valid_count = (
        total_items - len(invalid_ids)
    )

    return valid_count / total_items


def answer_contains_refusal(answer):
    """
    Check whether the model indicates that evidence
    is insufficient.
    """

    full_text = json.dumps(
        answer
    ).lower()

    refusal_phrases = [
        "insufficient evidence",
        "not enough evidence",
        "cannot determine",
        "insufficient information"
    ]

    return any(
        phrase in full_text
        for phrase in refusal_phrases
    )


def evaluate_question(item):

    print("\n" + "=" * 80)
    print(
        f"{item['id']}: "
        f"{item['question']}"
    )
    print("=" * 80)

    # ---------------------------------------------
    # Query understanding
    # ---------------------------------------------

    query_data = process_query(
        item["question"]
    )

    rewritten_query = query_data[
        "rewritten_query"
    ]

    print("\nRewritten query:")
    print(rewritten_query)

    # ---------------------------------------------
    # Retrieval
    # ---------------------------------------------

    results = retrieve(
        rewritten_query,
        top_candidates=10,
        final_results=3
    )

    if not results:

        print(
            "\nNo evidence retrieved."
        )

        return {
            "answer_point_coverage": 0,
            "citation_accuracy": 1.0,
            "refusal_correct": (
                not item["should_answer"]
            )
        }

    # ---------------------------------------------
    # Generate answer
    # ---------------------------------------------

    answer = generate_answer(
        item["question"],
        results
    )

    answer_text = json.dumps(
        answer
    )

    # ---------------------------------------------
    # Evaluate answer points
    # ---------------------------------------------

    coverage = check_answer_points(
        answer_text,
        item.get(
            "expected_answer_points",
            []
        )
    )

    if coverage is not None:

        print(
            f"\nAnswer point coverage: "
            f"{coverage:.2f}"
        )

    # ---------------------------------------------
    # Evaluate citations
    # ---------------------------------------------

    citation_accuracy = (
        validate_citations(
            answer,
            results
        )
    )

    print(
        f"Citation validity: "
        f"{citation_accuracy:.2f}"
    )

    # ---------------------------------------------
    # Evaluate refusal
    # ---------------------------------------------

    refused = answer_contains_refusal(
        answer
    )

    refusal_correct = True

    if item["should_answer"]:

        if refused:
            refusal_correct = False

    else:

        if not refused:
            refusal_correct = False

    print(
        f"Expected behavior: "
        f"{'ANSWER' if item['should_answer'] else 'REFUSE'}"
    )

    print(
        f"Refusal behavior: "
        f"{'PASS' if refusal_correct else 'FAIL'}"
    )

    # ---------------------------------------------
    # Print answer
    # ---------------------------------------------

    print("\nGenerated answer:")

    print(
        json.dumps(
            answer,
            indent=4
        )
    )

    return {
        "answer_point_coverage": coverage,
        "citation_accuracy": citation_accuracy,
        "refusal_correct": refusal_correct
    }


def main():

    questions = load_questions()

    evaluation_results = []

    for item in questions:

        result = evaluate_question(
            item
        )

        evaluation_results.append(
            result
        )

    # ---------------------------------------------
    # Overall metrics
    # ---------------------------------------------

    coverage_scores = [
        result["answer_point_coverage"]
        for result in evaluation_results
        if result["answer_point_coverage"]
        is not None
    ]

    citation_scores = [
        result["citation_accuracy"]
        for result in evaluation_results
    ]

    refusal_scores = [
        result["refusal_correct"]
        for result in evaluation_results
    ]

    print("\n" + "=" * 80)
    print("ANSWER EVALUATION SUMMARY")
    print("=" * 80)

    if coverage_scores:

        average_coverage = (
            sum(coverage_scores)
            / len(coverage_scores)
        )

        print(
            f"\nAverage answer point coverage: "
            f"{average_coverage:.2f}"
        )

    average_citations = (
        sum(citation_scores)
        / len(citation_scores)
    )

    print(
        f"Average citation validity: "
        f"{average_citations:.2f}"
    )

    refusal_accuracy = (
        sum(refusal_scores)
        / len(refusal_scores)
    )

    print(
        f"Refusal behavior accuracy: "
        f"{refusal_accuracy:.2f}"
    )


if __name__ == "__main__":
    main()