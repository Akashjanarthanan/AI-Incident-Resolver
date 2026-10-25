def clean_text(value):
    """
    Clean a text value.
    """

    if not isinstance(value, str):
        return ""

    value = value.strip()

    if not value:
        return ""

    return value


def rewrite_query(original_query, incident):
    """
    Build a compact search query using important
    technical signals from the structured incident.
    """

    parts = []

    error_code = clean_text(
        incident.get("error_code")
    )

    category = clean_text(
        incident.get("category")
    )

    technology = clean_text(
        incident.get("technology")
    )

    application = clean_text(
        incident.get("application")
    )

    environment = clean_text(
        incident.get("environment")
    )

    symptoms = incident.get(
        "symptoms",
        []
    )

    if error_code.lower() != "unknown":
        parts.append(error_code)

    if technology.lower() != "unknown":
        parts.append(technology)

    if category.lower() != "unknown":
        parts.append(category)

    if environment.lower() != "unknown":
        parts.append(environment)

    if application.lower() != "unknown":
        parts.append(application)

    if isinstance(symptoms, list):

        for symptom in symptoms:

            symptom = clean_text(symptom)

            if not symptom:
                continue

            if len(symptom.split()) < 2:
                continue

            parts.append(symptom)

    unique_parts = []
    seen = set()

    for part in parts:

        normalized = part.lower()

        if normalized not in seen:

            seen.add(normalized)
            unique_parts.append(part)

    rewritten_query = " ".join(
        unique_parts
    )

    if not rewritten_query:
        return original_query.strip()

    return rewritten_query