from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "all-MiniLM-L6-v2"

# Initial threshold.
# We will tune this using evaluation results.
GROUNDING_THRESHOLD = 0.80


class GroundingEvaluator:

    def __init__(self):

        print("Loading grounding evaluator...")

        self.model = SentenceTransformer(
            MODEL_NAME
        )

    def calculate_similarity(
        self,
        claim,
        evidence
    ):

        claim_embedding = self.model.encode(
            [claim]
        )

        evidence_embedding = self.model.encode(
            [evidence]
        )

        score = cosine_similarity(
            claim_embedding,
            evidence_embedding
        )[0][0]

        return float(score)

    def evaluate_claim(
        self,
        claim,
        evidence
    ):

        score = self.calculate_similarity(
            claim,
            evidence
        )

        supported = (
            score >= GROUNDING_THRESHOLD
        )

        return {
            "claim": claim,
            "similarity": score,
            "supported": supported
        }