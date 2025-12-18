import requests, uuid, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_idempotent_deduplication():
    eid = str(uuid.uuid4())
    event = {
        "topic": "orders",
        "event_id": eid,
        "timestamp": "2025-11-06T00:00:00Z",
        "source": "pytest",
        "payload": {"price": 100}
    }
    for _ in range(3):
        r = requests.post(f"{BASE}/publish", json=event)
        assert r.status_code == 200
