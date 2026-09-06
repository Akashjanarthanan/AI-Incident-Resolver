from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "all-MiniLM-L6-v2"


def main():
    model = SentenceTransformer(MODEL_NAME)

    sentences = [
        "Check whether the Oracle listener is running.",
        "Verify the database listener status.",
        "The weather is hot today."
    ]

    embeddings = model.encode(sentences)

    similarity = cosine_similarity(embeddings)

    print("\nSimilarity Matrix:\n")
    print(similarity)


if __name__ == "__main__":
    main()