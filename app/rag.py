import json

from conversation_memory import ConversationMemory
from incident_history import IncidentHistory
from incident_retriever import IncidentRetriever
from query_pipeline import process_query
from rag_retriever import retrieve
from confidence import calculate_confidence
from llm import generate_answer
from response_formatter import format_response
from query_router import route_query

def main():

    memory = ConversationMemory(
        max_messages=10
    )

    history = IncidentHistory()
    incident_retriever = IncidentRetriever()

    print("\n" + "=" * 70)
    print("AI INCIDENT RESOLVER")
    print("=" * 70)

    print(
        "\nType 'exit' to end the conversation."
    )

    while True:

        original_query = input(
            "\nEnter your incident:\n> "
        ).strip()

        if not original_query:
            print(
                "Please enter an incident."
            )
            continue

        if original_query.lower() == "exit":
            print(
                "\nConversation ended."
            )
            break

        conversation_history = (
            memory.get_formatted_history()
        )

        print(
            "\nAnalyzing incident..."
        )

        query_data = process_query(
            original_query,
            conversation_history
        )

        print(
            "\nStructured Incident:"
        )

        print(
            json.dumps(
                query_data["incident"],
                indent=4
            )
        )

        route = route_query(
            query_data["incident"]
        )

        print(
            "\nQuery Route:"
        )

        print(
            route["route"]
        )

        print(
            "\nRewritten Search Query:"
        )

        print(
            query_data["rewritten_query"]
        )

        print(
            "\nRetrieving relevant evidence..."
        )

        results = retrieve(
            query_data["rewritten_query"],
            incident=query_data["incident"],
            top_candidates=route[
                "top_candidates"
            ],
            final_results=route[
                "final_results"
            ]
        )
        print(
            "\nSearching previous incidents..."
        )

        previous_incidents = (
            incident_retriever.retrieve(
                query_data["rewritten_query"],
                top_k=3
            )
        )

        if previous_incidents:

            print(
                "\nSimilar Previous Incidents:"
            )

            for item in previous_incidents:
                print(
                    f"- Incident "
                    f"{item['incident_id']} "
                    f"(similarity: "
                    f"{item['similarity']:.4f})"
                )

        else:
            print(
                "\nNo similar previous incidents found."
            )

        if not results:

            response = (
                "Insufficient evidence in the "
                "knowledge base."
            )

            print(
                f"\n{response}"
            )

            memory.add_user_message(
                original_query
            )

            memory.add_assistant_message(
                response
            )

            continue

        confidence = calculate_confidence(
            results
        )

        print(
            f"\nRetrieval confidence: "
            f"{confidence['level']}"
        )

        print(
            f"Retrieval score: "
            f"{confidence['score']:.4f}"
        )

        if confidence["level"] == "LOW":

            response = (
                "Insufficient evidence in the "
                "knowledge base."
            )

            print(
                f"\n{response}"
            )

            memory.add_user_message(
                original_query
            )

            memory.add_assistant_message(
                response
            )

            continue

        print(
            "\nGenerating grounded response..."
        )

        answer = generate_answer(
    original_query,
    results,
    conversation_history,
    previous_incidents
)

        print(
            "\n" + "=" * 70
        )
        print(
            "AI RESPONSE"
        )
        print(
            "=" * 70
        )

        format_response(
            answer,
            results
        )

        # -------------------------------------------------
        # Save completed incident to persistent history
        # -------------------------------------------------

        incident_id = history.save_incident(
            query=original_query,
            incident=query_data["incident"],
            answer=answer
        )

        print(
            f"\nIncident saved successfully."
        )

        print(
            f"Incident ID: {incident_id}"
        )

        print(
            f"Total stored incidents: "
            f"{history.count()}"
        )

        # -------------------------------------------------
        # Update current conversation memory
        # -------------------------------------------------

        memory.add_user_message(
            original_query
        )

        memory.add_assistant_message(
            json.dumps(
                answer
            )
        )


if __name__ == "__main__":
    main()