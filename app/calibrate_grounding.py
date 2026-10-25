import json
from pathlib import Path

from grounding_evaluator import GroundingEvaluator


CALIBRATION_FILE = Path(
    "data/grounding_calibration.json"
)


def load_data():
    with open(
        CALIBRATION_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def evaluate_examples(
    evaluator,
    examples
):
    results = []

    for example in examples:

        score = evaluator.calculate_similarity(
            example["claim"],
            example["evidence"]
        )

        results.append(
            {
                "id": example["id"],
                "score": score,
                "expected": example["expected"]
            }
        )

        print(
            f"{example['id']} | "
            f"Expected={example['expected']} | "
            f"Score={score:.4f}"
        )

    return results


def calculate_metrics(
    results,
    threshold
):
    """
    Calculate classification metrics for
    a given similarity threshold.
    """

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0

    for result in results:

        predicted = (
            result["score"] >= threshold
        )

        expected = result["expected"]

        if predicted and expected:
            true_positive += 1

        elif not predicted and not expected:
            true_negative += 1

        elif predicted and not expected:
            false_positive += 1

        elif not predicted and expected:
            false_negative += 1

    total = len(results)

    accuracy = (
        (true_positive + true_negative)
        / total
        if total
        else 0
    )

    precision = (
        true_positive
        / (true_positive + false_positive)
        if (true_positive + false_positive)
        else 0
    )

    recall = (
        true_positive
        / (true_positive + false_negative)
        if (true_positive + false_negative)
        else 0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if (precision + recall)
        else 0
    )

    return {
        "threshold": threshold,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def main():

    examples = load_data()

    evaluator = GroundingEvaluator()

    print("\n" + "=" * 70)
    print("GROUNDING CALIBRATION")
    print("=" * 70)

    results = evaluate_examples(
        evaluator,
        examples
    )

    print("\n" + "=" * 70)
    print("THRESHOLD EVALUATION")
    print("=" * 70)

    best_result = None

    # Test thresholds from 0.20 to 0.90
    for i in range(20, 91, 5):

        threshold = i / 100

        metrics = calculate_metrics(
            results,
            threshold
        )

        print(
            f"\nThreshold: {metrics['threshold']:.2f}"
        )

        print(
            f"Accuracy : {metrics['accuracy']:.2f}"
        )

        print(
            f"Precision: {metrics['precision']:.2f}"
        )

        print(
            f"Recall   : {metrics['recall']:.2f}"
        )

        print(
            f"F1       : {metrics['f1']:.2f}"
        )

        if (
            best_result is None
            or metrics["f1"] > best_result["f1"]
        ):
            best_result = metrics

    print("\n" + "=" * 70)
    print("BEST THRESHOLD")
    print("=" * 70)

    print(
        f"\nThreshold: "
        f"{best_result['threshold']:.2f}"
    )

    print(
        f"Accuracy: "
        f"{best_result['accuracy']:.2f}"
    )

    print(
        f"Precision: "
        f"{best_result['precision']:.2f}"
    )

    print(
        f"Recall: "
        f"{best_result['recall']:.2f}"
    )

    print(
        f"F1: "
        f"{best_result['f1']:.2f}"
    )


if __name__ == "__main__":
    main()