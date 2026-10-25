import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import EMBEDDING_MODEL


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

HISTORY_PATH = Path(
    "data/incidents/incident_history.json"
)


# ---------------------------------------------------------
# Incident History Retriever
# ---------------------------------------------------------

class IncidentRetriever:

    def __init__(self):

        print(
            "\nLoading incident history retriever..."
        )

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )

        print(
            "Incident history retriever ready."
        )

    # -----------------------------------------------------
    # Load saved incidents
    # -----------------------------------------------------

    def load_incidents(self):

        if not HISTORY_PATH.exists():
            return []

        try:
            content = HISTORY_PATH.read_text(
                encoding="utf-8"
            )

            incidents = json.loads(
                content
            )

        except (
            json.JSONDecodeError,
            OSError
        ) as error:

            print(
                "Warning: Could not load incident "
                f"history: {error}"
            )

            return []

        if not isinstance(
            incidents,
            list
        ):
            print(
                "Warning: Incident history must "
                "contain a JSON list."
            )

            return []

        return [
            incident
            for incident in incidents
            if isinstance(incident, dict)
        ]

    # -----------------------------------------------------
    # Retrieve similar previous incidents
    # -----------------------------------------------------

    def retrieve(
        self,
        query,
        top_k=3
    ):

        query = str(
            query or ""
        ).strip()

        if not query:
            return []

        if top_k <= 0:
            return []

        incidents = self.load_incidents()

        if not incidents:
            return []

        # Prepare searchable text for every incident.
        searchable_texts = []

        for incident in incidents:

            original_query = incident.get(
                "query",
                ""
            )

            incident_details = incident.get(
                "incident",
                {}
            )

            if not isinstance(
                incident_details,
                dict
            ):
                incident_details = {}

            searchable_text = (
                str(original_query)
                + " "
                + json.dumps(
                    incident_details,
                    ensure_ascii=False
                )
            )

            searchable_texts.append(
                searchable_text
            )

        # Encode the current query.
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        )

        # Encode previous incidents in one batch.
        incident_embeddings = self.model.encode(
            searchable_texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        # Calculate similarity between the current query
        # and each previous incident.
        similarity_scores = cosine_similarity(
            query_embedding,
            incident_embeddings
        )[0]

        candidates = []

        for index, incident in enumerate(
            incidents
        ):

            score = float(
                similarity_scores[index]
            )

            answer = incident.get(
                "answer",
                {}
            )

            if not isinstance(
                answer,
                dict
            ):
                answer = {}

            candidate = {
                "incident_id": incident.get(
                    "incident_id"
                ),
                "timestamp": incident.get(
                    "timestamp"
                ),
                "query": incident.get(
                    "query",
                    ""
                ),
                "incident": incident.get(
                    "incident",
                    {}
                ),
                "answer": answer,
                "similarity": score
            }

            candidates.append(
                candidate
            )

        # Highest similarity first.
        candidates.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return candidates[:top_k]


# ---------------------------------------------------------
# Standalone Test
# ---------------------------------------------------------

def main():

    retriever = IncidentRetriever()

    query = input(
        "\nEnter incident to search:\n> "
    ).strip()

    results = retriever.retrieve(
        query,
        top_k=3
    )

    print(
        "\nSimilar Previous Incidents:"
    )

    if not results:

        print(
            "No previous incidents found."
        )

        return

    for result in results:

        print(
            "\n" + "-" * 60
        )

        print(
            f"Incident ID: "
            f"{result['incident_id']}"
        )

        print(
            f"Similarity: "
            f"{result['similarity']:.4f}"
        )

        print(
            f"Query: "
            f"{result['query']}"
        )

        answer = result.get(
            "answer"
        ) or {}

        likely_cause = answer.get(
            "likely_cause",
            "unknown"
        )

        print(
            f"Likely Cause: {likely_cause}"
        )


if __name__ == "__main__":

    main()