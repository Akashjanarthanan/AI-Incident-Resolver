import json
from pathlib import Path

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

INDEX_PATH = Path("vector_store/knowledge_base.index")
METADATA_PATH = Path("vector_store/metadata.json")


def load_vector_store():
    """Load FAISS index and chunk metadata."""

    index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    return index, metadata


def create_bm25(metadata):
    """Create a BM25 keyword search index."""

    documents = [
        item["text"]
        for item in metadata
    ]

    tokenized_documents = [
        document.lower().split()
        for document in documents
    ]

    return BM25Okapi(tokenized_documents)


def semantic_search(query, model, index, metadata, top_k=5):
    """Retrieve documents using embedding similarity."""

    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for rank, vector_id in enumerate(indices[0], start=1):

        results.append(
            {
                "vector_id": int(vector_id),
                "rank": rank,
                "score": float(distances[0][rank - 1]),
                "source": metadata[vector_id]["source"],
                "chunk_id": metadata[vector_id]["chunk_id"],
                "text": metadata[vector_id]["text"],
            }
        )

    return results


def keyword_search(query, bm25, metadata, top_k=5):
    """Retrieve documents using BM25 keyword matching."""

    query_tokens = query.lower().split()

    scores = bm25.get_scores(query_tokens)

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for rank, vector_id in enumerate(top_indices, start=1):

        results.append(
            {
                "vector_id": int(vector_id),
                "rank": rank,
                "score": float(scores[vector_id]),
                "source": metadata[vector_id]["source"],
                "chunk_id": metadata[vector_id]["chunk_id"],
                "text": metadata[vector_id]["text"],
            }
        )

    return results


def reciprocal_rank_fusion(
    semantic_results,
    keyword_results,
    k=60
):
    """
    Combine rankings from semantic and keyword retrieval.

    RRF does not require the two retrieval systems
    to have comparable score scales.
    """

    fused_scores = {}
    documents = {}

    for result in semantic_results:

        vector_id = result["vector_id"]

        fused_scores[vector_id] = (
            fused_scores.get(vector_id, 0)
            + 1 / (k + result["rank"])
        )

        documents[vector_id] = result

    for result in keyword_results:

        vector_id = result["vector_id"]

        fused_scores[vector_id] = (
            fused_scores.get(vector_id, 0)
            + 1 / (k + result["rank"])
        )

        documents[vector_id] = result

    sorted_ids = sorted(
        fused_scores,
        key=fused_scores.get,
        reverse=True
    )

    results = []

    for rank, vector_id in enumerate(sorted_ids, start=1):

        result = documents[vector_id].copy()

        result["hybrid_rank"] = rank
        result["hybrid_score"] = fused_scores[vector_id]

        results.append(result)

    return results


def main():

    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Loading FAISS index...")

    index, metadata = load_vector_store()

    print("Creating BM25 index...")

    bm25 = create_bm25(metadata)

    query = input("\nEnter your incident/question: ")

    semantic_results = semantic_search(
        query,
        model,
        index,
        metadata,
        top_k=5
    )

    keyword_results = keyword_search(
        query,
        bm25,
        metadata,
        top_k=5
    )

    hybrid_results = reciprocal_rank_fusion(
        semantic_results,
        keyword_results
    )

    print("\n" + "=" * 70)
    print("HYBRID SEARCH RESULTS")
    print("=" * 70)

    for result in hybrid_results[:5]:

        print(f"\nHybrid Rank : {result['hybrid_rank']}")
        print(f"Source      : {result['source']}")
        print(f"Chunk       : {result['chunk_id']}")
        print(f"Hybrid Score: {result['hybrid_score']:.4f}")

        print("\nContent:")
        print(result["text"][:500])
        print("-" * 70)


if __name__ == "__main__":
    main()