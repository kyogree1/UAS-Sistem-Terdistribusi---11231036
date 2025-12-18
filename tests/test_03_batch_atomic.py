import requests, uuid, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_batch_atomic_transaction():
    batch = {
        "events": [
            {
                "topic": "batch",
                "event_id": str(uuid.uuid4()),
                "timestamp": "2025-11-06T00:00:00Z",
                "source": "pytest",
                "payload": {"i": i}
            } for i in range(5)
        ]
    }
    r = requests.post(f"{BASE}/publish", json=batch)
    assert r.status_code == 200
