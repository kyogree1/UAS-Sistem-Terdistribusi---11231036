import requests, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_same_event_id_different_topic():
    eid = "shared-id"
    e1 = {
        "topic": "A",
        "event_id": eid,
        "timestamp": "2025-11-06T00:00:00Z",
        "source": "pytest",
        "payload": {"x": 1}
    }
    e2 = {
        "topic": "B",
        "event_id": eid,
        "timestamp": "2025-11-06T00:00:00Z",
        "source": "pytest",
        "payload": {"x": 2}
    }
    assert requests.post(f"{BASE}/publish", json=e1).status_code == 200
    assert requests.post(f"{BASE}/publish", json=e2).status_code == 200
