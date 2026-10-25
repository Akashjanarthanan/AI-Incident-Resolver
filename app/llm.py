from incident_retriever import IncidentRetriever
import json

import ollama

from config import (
    OLLAMA_MODEL,
    OLLAMA_HOST
)


ollama_client = ollama.Client(
    host=OLLAMA_HOST
)


def generate_answer(
    query,
    retrieved_context,
    conversation_history=None,
    previous_incidents=None
):
    if conversation_history:
        history_text = conversation_history
    else:
        history_text = "No previous conversation."
    context = "\n\n".join(
        [
            (
                f"SOURCE_ID: {index}\n"
                f"SOURCE: {item['source']}\n"
                f"CHUNK_ID: {item['chunk_id']}\n"
                f"CONTENT:\n{item['text']}"
            )
            for index, item in enumerate(retrieved_context)
        ]
    )
    if previous_incidents:
        incident_history_text = ""

        for item in previous_incidents:
            incident_history_text += f"""
Previous Incident ID: {item.get('incident_id')}
Previous Query: {item.get('query')}
Previous Incident:
{json.dumps(item.get('incident', {}), indent=2)}

Previous Resolution:
{json.dumps(item.get('answer', {}), indent=2)}

Similarity:
{item.get('similarity', 0.0):.4f}

---
"""
    else:
        incident_history_text = (
            "No similar previous incidents found."
        )

    prompt = f"""
You are an AI Incident Resolver for an IT support team.

Analyze the incident using ONLY the supplied knowledge-base evidence.

STRICT RULES:

1. Never invent facts.
2. Never invent troubleshooting steps.
3. Every recommendation must be supported by one or more supplied sources.
4. Use source IDs exactly as provided.
5. If evidence is insufficient, set confidence to "LOW".
6. Never claim an action was performed.
7. Do not use outside knowledge.

Previous Similar Incidents:
{incident_history_text}

Rules for previous incidents:

1. Previous incidents are supplementary evidence only.

2. Do not assume a previous incident has exactly the
   same root cause as the current incident.

3. Use previous incidents only when they are relevant.

4. Do not invent facts that are not present in the
   current evidence or previous incident records.

5. Clearly distinguish current knowledge-base evidence
   from previous incident experience.

Previous conversation:
{history_text}
INCIDENT:
{query}

KNOWLEDGE BASE:
{context}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "incident_summary": "string",
    "likely_cause": "string",
    "confidence": "HIGH | MEDIUM | LOW",
    "evidence": [
        {{
            "statement": "string",
            "source_id": 0
        }}
    ],
    "investigation_steps": [
        {{
            "step": "string",
            "source_id": 0
        }}
    ],
    "recommended_resolution": [
        {{
            "action": "string",
            "source_id": 0
        }}
    ],
    "warnings": [
        "string"
    ]
}}

If the evidence is insufficient, do not invent a solution.
"""


    response = ollama_client.chat(
    model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],format="json",
    )

    raw_output = response["message"]["content"].strip()

    try:
        return json.loads(raw_output)

    except json.JSONDecodeError:
        raise ValueError(
            "The LLM did not return valid JSON.\n\n"
            f"Raw response:\n{raw_output}"
        )