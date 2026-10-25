import json
import re
import ollama

from config import (
    OLLAMA_MODEL,
    OLLAMA_HOST
)

# Initialize Ollama client after importing configuration
ollama_client = ollama.Client(
    host=OLLAMA_HOST
)

# ---------------------------------------------------------
# 1. Deterministic Error Code Extraction
# ---------------------------------------------------------

def extract_error_code(query):
    pattern = r"\bORA[-\s]?(\d{5})\b"

    match = re.search(
        pattern,
        query,
        re.IGNORECASE
    )

    if not match:
        return "unknown"

    return f"ORA-{match.group(1)}"


# ---------------------------------------------------------
# 2. Deterministic Environment Extraction
# ---------------------------------------------------------

def extract_environment(query):
    query_lower = query.lower()

    if re.search(
        r"\b(prod|production)\b",
        query_lower
    ):
        return "production"

    if re.search(
        r"\b(dev|development)\b",
        query_lower
    ):
        return "development"

    if re.search(
        r"\b(qa|test|testing)\b",
        query_lower
    ):
        return "testing"

    if re.search(
        r"\b(stage|staging)\b",
        query_lower
    ):
        return "staging"

    return "unknown"


# ---------------------------------------------------------
# 3. Deterministic Domain / Technology Extraction
# ---------------------------------------------------------

def extract_domain_metadata(query):
    text = query.lower()

    category = "unknown"
    technology = "unknown"

    # Oracle / Database
    if any(
        term in text
        for term in [
            "oracle",
            "ora-",
            "ora "
        ]
    ):
        category = "database"
        technology = "oracle"

    # Firewall / Network
    elif any(
        term in text
        for term in [
            "firewall",
            "tcp port",
            "network traffic"
        ]
    ):
        category = "network"
        technology = "network"

    # DNS
    elif any(
        term in text
        for term in [
            "dns",
            "hostname",
            "name resolution"
        ]
    ):
        category = "network"
        technology = "dns"

    # Deployment
    elif any(
        term in text
        for term in [
            "deployment",
            "deploy",
            "rollback"
        ]
    ):
        category = "deployment"
        technology = "application"

    # Application Timeout
    elif any(
        term in text
        for term in [
            "timeout",
            "request timeout"
        ]
    ):
        category = "application"
        technology = "application"

    # API
    elif any(
        term in text
        for term in [
            "api",
            "http 500",
            "500 error",
            "internal server error"
        ]
    ):
        category = "application"
        technology = "api"

    return {
        "category": category,
        "technology": technology
    }


# ---------------------------------------------------------
# 4. Application Normalization
# ---------------------------------------------------------

def normalize_application(application):
    if not application:
        return "unknown"

    application = str(
        application
    ).strip()

    if not application:
        return "unknown"

    normalized = application.lower().strip()

    invalid_values = {
        "unknown",
        "oracle",
        "oracle database",
        "database",
        "db",
        "listener",
        "oracle listener",
        "deployment",
        "deploy",
        "prod",
        "production",
        "prod deploy",
        "production deploy",
        "network",
        "dns",
        "firewall",
        "application"
    }

    if normalized in invalid_values:
        return "unknown"

    return application


# ---------------------------------------------------------
# 5. Symptom Normalization
# ---------------------------------------------------------

def normalize_symptoms(symptoms):
    if not symptoms:
        return []

    if isinstance(
        symptoms,
        str
    ):
        symptoms = [symptoms]

    cleaned = []

    for symptom in symptoms:
        if not symptom:
            continue

        symptom = str(
            symptom
        ).strip()

        if not symptom:
            continue

        if symptom not in cleaned:
            cleaned.append(symptom)

    return cleaned[:3]


# ---------------------------------------------------------
# 6. Intent Normalization
# ---------------------------------------------------------

def normalize_intent(intent):
    if not intent:
        return "unknown"

    intent = str(
        intent
    ).strip().lower()

    valid_intents = {
        "troubleshooting",
        "resolution",
        "information"
    }

    if intent in valid_intents:
        return intent

    return "unknown"


# ---------------------------------------------------------
# 7. LLM Natural Language Extraction
# ---------------------------------------------------------

def analyze_with_llm(
    query,
    conversation_history=None
):
    """
    Analyze an incident using:
    - deterministic Python extraction
    - Ollama LLM extraction
    - validation / normalization

    Important:
    The LLM is ONLY responsible for:
    - application
    - symptoms
    - intent

    Error code, environment, category and technology
    are extracted deterministically.
    """

    # Deterministic extraction
    error_code = extract_error_code(
        query
    )

    environment = extract_environment(
        query
    )

    domain_metadata = extract_domain_metadata(
        query
    )

    category = domain_metadata["category"]
    technology = domain_metadata["technology"]

    # Conversation history
    if conversation_history:
        history_text = conversation_history
    else:
        history_text = (
            "No previous conversation."
        )

    # -----------------------------------------------------
    # LLM Prompt
    # -----------------------------------------------------

    prompt = f"""
You are an IT incident classification assistant.

Analyze the CURRENT user query using the previous conversation when useful.

Previous conversation:
{history_text}

Current query:
{query}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "application": "string",
    "symptoms": [
        "string"
    ],
    "intent": "troubleshooting | resolution | information | unknown"
}}

Rules:

1. Do NOT treat "Oracle", "database", "DB", "listener",
   "deployment", "prod", "production", "network", "DNS",
   or "firewall" as an application name.

2. The application should be the actual application/service
   name only when it is explicitly present.

3. Do not invent an application name.

4. Symptoms should describe the actual problem reported by
   the user.

5. Keep symptoms concise.

6. Use the previous conversation to understand short
   follow-up questions such as:
   "It is already running"
   "What should I check next?"
   "The port is open"

7. Intent meanings:
   - troubleshooting = investigating a problem
   - resolution = asking how to fix the problem
   - information = asking for general information

8. When something is unknown, return "unknown".

9. Do not include explanations outside the JSON.

Example 1:

User:
Application cannot connect to Oracle after deployment.
Error ORA-12541.

JSON:
{{
    "application": "unknown",
    "symptoms": [
        "application cannot connect to Oracle after deployment"
    ],
    "intent": "troubleshooting"
}}

Example 2:

User:
The listener is already running.

JSON:
{{
    "application": "unknown",
    "symptoms": [
        "Oracle listener is already running"
    ],
    "intent": "troubleshooting"
}}

Example 3:

User:
What should I check next?

JSON:
{{
    "application": "unknown",
    "symptoms": [
        "user wants the next troubleshooting step"
    ],
    "intent": "troubleshooting"
}}
"""

    # -----------------------------------------------------
    # Call Ollama
    # -----------------------------------------------------

    response = ollama_client.chat(
    model=OLLAMA_MODEL,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    format="json"
)

    # -----------------------------------------------------
    # Parse LLM Response
    # -----------------------------------------------------

    raw_content = (
        response["message"]["content"]
    )

    try:
        llm_result = json.loads(
            raw_content
        )

    except json.JSONDecodeError:
        print(
            "\nWarning: LLM returned invalid JSON."
        )

        llm_result = {
            "application": "unknown",
            "symptoms": [
                query
            ],
            "intent": "unknown"
        }

    # -----------------------------------------------------
    # Normalize LLM Output
    # -----------------------------------------------------

    application = normalize_application(
        llm_result.get(
            "application"
        )
    )

    symptoms = normalize_symptoms(
        llm_result.get(
            "symptoms"
        )
    )

    intent = normalize_intent(
        llm_result.get(
            "intent"
        )
    )

    # -----------------------------------------------------
    # Final Structured Incident
    # -----------------------------------------------------

    return {
        "error_code": error_code,
        "application": application,
        "environment": environment,
        "category": category,
        "technology": technology,
        "symptoms": symptoms,
        "intent": intent
    }


# ---------------------------------------------------------
# 8. Public Analyzer Function
# ---------------------------------------------------------

def analyze_incident(
    query,
    conversation_history=None
):
    return analyze_with_llm(
        query,
        conversation_history
    )


# ---------------------------------------------------------
# 9. Standalone Test
# ---------------------------------------------------------

def main():

    query = input(
        "\nEnter incident:\n> "
    ).strip()

    print(
        "\nAnalyzing incident..."
    )

    result = analyze_incident(
        query
    )

    print(
        "\nStructured Incident:"
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )


if __name__ == "__main__":
    main()