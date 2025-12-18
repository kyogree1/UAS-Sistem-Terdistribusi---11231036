import requests, uuid, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_large_payload_insert():
    eid = str(uuid.uuid4())
    event = {
        "topic": "large",
        "event_id": eid,
        "timestamp": "2025-11-06T00:00:00Z",
        "source": "pytest",
        "payload": {"blob": "x" * 1_000_000}
    }
    r = requests.post(f"{BASE}/publish", json=event)
    assert r.status_code == 200
