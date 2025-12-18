import requests, uuid, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_partial_batch_rollback():
    batch = {
        "events": [
            {
                "topic": "rollback",
                "event_id": str(uuid.uuid4()),
                "timestamp": "2025-11-06T00:00:00Z",
                "source": "pytest",
                "payload": {"ok": 1}
            },
            {
                "topic": "rollback",
                "event_id": "bad",
                "timestamp": "2025-11-06T00:00:00Z",
                "source": "pytest",
                "payload": "invalid"
            }
        ]
    }
    r = requests.post(f"{BASE}/publish", json=batch)
    assert r.status_code in (400, 422)
