import json

from pathlib import Path
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config import (
    MAX_CONVERSATION_MESSAGES,
    TOP_PREVIOUS_INCIDENTS
)
from logger import logger

from conversation_memory import ConversationMemory
from incident_history import IncidentHistory
from incident_retriever import IncidentRetriever
from query_pipeline import process_query
from rag_retriever import retrieve
from confidence import calculate_confidence
from llm import generate_answer
from query_router import route_query


# ---------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------

app = FastAPI(
    title="AI Incident Resolver",
    description="RAG-based IT Incident Resolution API",
    version="1.0.0"
)

FRONTEND_DIR = (
    Path(__file__).resolve().parent.parent
    / "frontend"
)

app.mount(
    "/ui",
    StaticFiles(
        directory=str(FRONTEND_DIR),
        html=True
    ),
    name="frontend"
)	
# ---------------------------------------------------------
# Global Services
# ---------------------------------------------------------

incident_retriever = IncidentRetriever()
incident_history = IncidentHistory()


# ---------------------------------------------------------
# Session Memory
# ---------------------------------------------------------

session_memories = {}

def get_session_memory(session_id):
    if session_id not in session_memories:
        session_memories[session_id] = ConversationMemory(
            max_messages=MAX_CONVERSATION_MESSAGES
        )

    return session_memories[session_id]



# ---------------------------------------------------------
# Request Model
# ---------------------------------------------------------

class IncidentRequest(BaseModel):

    query: str

    session_id: str = "default"


# ---------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------

@app.get("/")
def root():

    return {
        "service": "AI Incident Resolver",
        "status": "running",
        "docs": "/docs"
    }


# ---------------------------------------------------------
# Health Endpoint
# ---------------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "AI Incident Resolver"
    }


# ---------------------------------------------------------
# Resolve Incident
# ---------------------------------------------------------

@app.post("/resolve")
def resolve_incident(
    request: IncidentRequest
):

    original_query = request.query.strip()

    if not original_query:

        return {
            "status": "error",
            "message": "Query cannot be empty."
        }

    # -----------------------------------------------------
    # Get Session Memory
    # -----------------------------------------------------

    memory = get_session_memory(
        request.session_id
    )

    conversation_history = (
        memory.get_formatted_history()
    )

    # -----------------------------------------------------
    # Query Understanding
    # -----------------------------------------------------

    query_data = process_query(
        original_query,
        conversation_history
    )

    incident = query_data["incident"]

    # -----------------------------------------------------
    # Query Routing
    # -----------------------------------------------------

    route = route_query(
        incident
    )

    # -----------------------------------------------------
    # Knowledge Base Retrieval
    # -----------------------------------------------------

    results = retrieve(
        query_data["rewritten_query"],
        incident=incident,
        top_candidates=route["top_candidates"],
        final_results=route["final_results"]
    )

    if not results:

        response = (
            "Insufficient evidence in the knowledge base."
        )

        memory.add_user_message(
            original_query
        )

        memory.add_assistant_message(
            response
        )

        return {
            "status": "insufficient_evidence",
            "session_id": request.session_id,
            "incident": incident
        }

    # -----------------------------------------------------
    # Retrieval Confidence
    # -----------------------------------------------------

    confidence = calculate_confidence(
        results
    )

    if confidence["level"] == "LOW":

        response = (
            "Insufficient evidence in the knowledge base."
        )

        memory.add_user_message(
            original_query
        )

        memory.add_assistant_message(
            response
        )

        return {
            "status": "insufficient_evidence",
            "session_id": request.session_id,
            "incident": incident,
            "retrieval_confidence": confidence
        }

    # -----------------------------------------------------
    # Previous Incident Retrieval
    # -----------------------------------------------------

    previous_incidents = (
        incident_retriever.retrieve(
            query_data["rewritten_query"],
            top_k=TOP_PREVIOUS_INCIDENTS
        )
    )

    # -----------------------------------------------------
    # Generate Grounded Answer
    # -----------------------------------------------------

    answer = generate_answer(
        original_query,
        results,
        conversation_history,
        previous_incidents
    )

    # -----------------------------------------------------
    # Save to Persistent Incident History
    # -----------------------------------------------------

    incident_id = incident_history.save_incident(
        query=original_query,
        incident=incident,
        answer=answer
    )

    # -----------------------------------------------------
    # Update Session Memory
    # -----------------------------------------------------

    memory.add_user_message(
        original_query
    )

    memory.add_assistant_message(
        json.dumps(answer)
    )

    # -----------------------------------------------------
    # Final Response
    # -----------------------------------------------------

    return {
        "status": "success",
        "session_id": request.session_id,
        "incident_id": incident_id,
        "incident": incident,
        "route": route["route"],
        "rewritten_query": query_data[
            "rewritten_query"
        ],
        "retrieval_confidence": confidence,
        "knowledge_base_results": results,
        "previous_incidents": previous_incidents,
        "answer": answer,
        "conversation_messages": len(
            memory.get_messages()
        )
    }


# ---------------------------------------------------------
# Get All Incident History
# ---------------------------------------------------------

@app.get("/history")
def get_incident_history():

    incidents = incident_history.get_all()

    return {
        "total_incidents": len(incidents),
        "incidents": incidents
    }


# ---------------------------------------------------------
# Get One Incident
# ---------------------------------------------------------

@app.get("/history/{incident_id}")
def get_incident(
    incident_id: int
):

    incidents = incident_history.get_all()

    for incident in incidents:

        if incident.get(
            "incident_id"
        ) == incident_id:

            return incident

    raise HTTPException(
        status_code=404,
        detail=f"Incident {incident_id} not found."
    )