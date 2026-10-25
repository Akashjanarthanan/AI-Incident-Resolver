import json
from pathlib import Path
from datetime import datetime


HISTORY_PATH = Path(
    "data/incidents/incident_history.json"
)


class IncidentHistory:

    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        HISTORY_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not HISTORY_PATH.exists():
            HISTORY_PATH.write_text(
                "[]",
                encoding="utf-8"
            )

    def _load(self):
        try:
            return json.loads(
                HISTORY_PATH.read_text(
                    encoding="utf-8"
                )
            )
        except (
            json.JSONDecodeError,
            FileNotFoundError
        ):
            return []

    def _save(self, incidents):
        HISTORY_PATH.write_text(
            json.dumps(
                incidents,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

    def save_incident(
        self,
        query,
        incident,
        answer
    ):
        incidents = self._load()

        record = {
            "incident_id": len(incidents) + 1,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "incident": incident,
            "answer": answer
        }

        incidents.append(record)

        self._save(incidents)

        return record["incident_id"]

    def get_all(self):
        return self._load()

    def count(self):
        return len(
            self._load()
        )


def main():

    history = IncidentHistory()

    incident = {
        "error_code": "ORA-12541",
        "application": "unknown",
        "environment": "production",
        "category": "database",
        "technology": "oracle",
        "symptoms": [
            "application cannot connect to Oracle"
        ],
        "intent": "troubleshooting"
    }

    answer = {
        "incident_summary":
            "Application cannot connect to Oracle.",
        "likely_cause":
            "Oracle listener connectivity issue.",
        "confidence":
            "HIGH"
    }

    incident_id = history.save_incident(
        query=(
            "Application cannot connect to Oracle "
            "after deployment. Error ORA-12541."
        ),
        incident=incident,
        answer=answer
    )

    print(
        f"\nIncident saved successfully."
    )

    print(
        f"Incident ID: {incident_id}"
    )

    print(
        f"Total incidents: {history.count()}"
    )


if __name__ == "__main__":
    main()