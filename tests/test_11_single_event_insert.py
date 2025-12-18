import requests, uuid, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_single_event_insert():
    eid = str(uuid.uuid4())
    event = {
        "topic": "single",
        "event_id": eid,
        "timestamp": "2025-11-06T00:00:00Z",
        "source": "pytest",
        "payload": {"ok": True}
    }
    r = requests.post(f"{BASE}/publish", json=event)
    assert r.status_code == 200
