import json
from pathlib import Path



import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder,
)

from metadata_filter import filter_metadata


EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

RERANKER_MODEL_NAME = (
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

INDEX_PATH = Path(
    "vector_store/knowledge_base.index"
)

METADATA_PATH = Path(
    "vector_store/metadata.json"
)

from config import (
    EMBEDDING_MODEL as CONFIG_EMBEDDING_MODEL,
    RERANKER_MODEL as CONFIG_RERANKER_MODEL
)

class RetrievalEngine:

    def __init__(self):

        print("Loading embedding model...")

        self.embedding_model = SentenceTransformer(
            CONFIG_EMBEDDING_MODEL
        )

        print("Loading reranker...")

        self.reranker = CrossEncoder(
            CONFIG_RERANKER_MODEL
        )

        print("Loading FAISS index...")

        self.index = faiss.read_index(
            str(INDEX_PATH)
        )

        print("Loading metadata...")

        with open(
            METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            self.metadata = json.load(file)

        print("Creating BM25 index...")

        documents = [
            item["text"]
            for item in self.metadata
        ]

        tokenized_documents = [
            document.lower().split()
            for document in documents
        ]

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

        print("Retrieval engine ready.")

    def semantic_search(
        self,
        query,
        top_k=10
    ):

        query_embedding = (
            self.embedding_model.encode(
                [query]
            )
        )

        query_embedding = np.array(
            query_embedding
        ).astype("float32")

        distances, indices = (
            self.index.search(
                query_embedding,
                top_k
            )
        )

        results = []

        for rank, vector_id in enumerate(
            indices[0],
            start=1
        ):

            results.append(
                {
                    "vector_id": int(vector_id),
                    "rank": rank,
                    "score": float(
                        distances[0][rank - 1]
                    ),
                    "source": self.metadata[
                        vector_id
                    ]["source"],
                    "chunk_id": self.metadata[
                        vector_id
                    ]["chunk_id"],
                    "text": self.metadata[
                        vector_id
                    ]["text"],
                    "category": self.metadata[
                        vector_id
                    ].get("category", "unknown"),
                    "technology": self.metadata[
                        vector_id
                    ].get("technology", "unknown"),
                    "document_type": self.metadata[
                        vector_id
                    ].get("document_type", "unknown"),
                    "environment": self.metadata[
                        vector_id
                    ].get("environment", "general"),
                }
            )

        return results

    def keyword_search(
        self,
        query,
        top_k=10
    ):

        query_tokens = (
            query.lower().split()
        )

        scores = self.bm25.get_scores(
            query_tokens
        )

        top_indices = np.argsort(
            scores
        )[::-1][:top_k]

        results = []

        for rank, vector_id in enumerate(
            top_indices,
            start=1
        ):

            results.append(
                {
                    "vector_id": int(vector_id),
                    "rank": rank,
                    "score": float(
                        scores[vector_id]
                    ),
                    "source": self.metadata[
                        vector_id
                    ]["source"],
                    "chunk_id": self.metadata[
                        vector_id
                    ]["chunk_id"],
                    "text": self.metadata[
                        vector_id
                    ]["text"],
                    "category": self.metadata[
                        vector_id
                    ].get("category", "unknown"),
                    "technology": self.metadata[
                        vector_id
                    ].get("technology", "unknown"),
                    "document_type": self.metadata[
                        vector_id
                    ].get("document_type", "unknown"),
                    "environment": self.metadata[
                        vector_id
                    ].get("environment", "general"),
                }
            )

        return results

    def hybrid_search(
        self,
        query,
        top_k=10
    ):

        semantic_results = (
            self.semantic_search(
                query,
                top_k
            )
        )

        keyword_results = (
            self.keyword_search(
                query,
                top_k
            )
        )

        scores = {}
        documents = {}

        rrf_k = 60

        for result in semantic_results:

            vector_id = result[
                "vector_id"
            ]

            scores[vector_id] = (
                scores.get(vector_id, 0)
                + 1
                / (
                    rrf_k
                    + result["rank"]
                )
            )

            documents[vector_id] = result

        for result in keyword_results:

            vector_id = result[
                "vector_id"
            ]

            scores[vector_id] = (
                scores.get(vector_id, 0)
                + 1
                / (
                    rrf_k
                    + result["rank"]
                )
            )

            documents[vector_id] = result

        ranked_ids = sorted(
            scores,
            key=scores.get,
            reverse=True
        )

        return [
            documents[vector_id]
            for vector_id in ranked_ids[:top_k]
        ]

    def rerank(
        self,
        query,
        candidates,
        top_k=3
    ):

        if not candidates:
            return []

        pairs = [
            (
                query,
                candidate["text"]
            )
            for candidate in candidates
        ]

        scores = self.reranker.predict(
            pairs
        )

        results = []

        for candidate, score in zip(
            candidates,
            scores
        ):

            result = candidate.copy()

            result["reranker_score"] = (
                float(score)
            )

            results.append(result)

        results.sort(
            key=lambda item:
            item["reranker_score"],
            reverse=True
        )

        return results[:top_k]

    def retrieve(
        self,
        query,
        category=None,
        technology=None,
        environment=None,
        top_candidates=10,
        final_results=3
    ):
        """
        Full retrieval pipeline:

        1. Hybrid retrieval
        2. Metadata filtering
        3. CrossEncoder reranking
        """

        candidates = self.hybrid_search(
            query,
            top_candidates
        )

        filtered_candidates = (
            filter_metadata(
                candidates,
                category=category,
                technology=technology,
                environment=environment
            )
        )

        # Safety fallback:
        # if metadata filtering removes everything,
        # use the original candidates.
        if not filtered_candidates:
            filtered_candidates = candidates

        return self.rerank(
            query,
            filtered_candidates,
            final_results
        )