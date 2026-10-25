import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

INDEX_PATH = Path("vector_store/knowledge_base.index")
METADATA_PATH = Path("vector_store/metadata.json")


def load_vector_store():

    index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    return index, metadata


def search(query, model, index, metadata, top_k=3):

    query_embedding = model.encode([query])

    query_embedding = np.array(
        query_embedding
    ).astype("float32")

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for rank, vector_id in enumerate(indices[0], start=1):

        results.append(
            {
                "rank": rank,
                "distance": float(distances[0][rank - 1]),
                "source": metadata[vector_id]["source"],
                "chunk_id": metadata[vector_id]["chunk_id"],
                "text": metadata[vector_id]["text"],
            }
        )

    return results


def main():

    print("Loading model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Loading vector store...")

    index, metadata = load_vector_store()

    query = input("\nEnter your incident/question: ")

    results = search(
        query,
        model,
        index,
        metadata,
        top_k=3
    )

    print("\n" + "=" * 70)
    print("SEARCH RESULTS")
    print("=" * 70)

    for result in results:

        print(f"\nRank: {result['rank']}")
        print(f"Source: {result['source']}")
        print(f"Chunk: {result['chunk_id']}")
        print(f"Distance: {result['distance']}")
        print("\nContent:")
        print(result["text"])


if __name__ == "__main__":
    main()