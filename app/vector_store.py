import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


def main():
    model = SentenceTransformer(MODEL_NAME)

    documents = [
        "Check whether the Oracle listener is running.",
        "Verify the database listener status.",
        "The application server communicates with the database.",
        "The weather is hot today."
    ]

    # Convert documents into embeddings
    embeddings = model.encode(documents)

    # Convert embeddings to float32 because FAISS expects it
    embeddings = np.array(embeddings).astype("float32")

    # Create FAISS index
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    # Add embeddings to the index
    index.add(embeddings)

    print(f"Number of vectors in FAISS: {index.ntotal}")

    # User query
    query = "How can I verify the Oracle database listener?"

    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    # Search top 2 results
    distances, indices = index.search(query_embedding, k=2)

    print("\nUser Query:")
    print(query)

    print("\nSearch Results:")

    for rank, index_number in enumerate(indices[0], start=1):
        print(f"\nRank {rank}")
        print(f"Document: {documents[index_number]}")
        print(f"Distance: {distances[0][rank - 1]}")


if __name__ == "__main__":
    main()