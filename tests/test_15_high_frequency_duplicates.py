import requests, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_high_frequency_duplicates():
    eid = "spam"
    event = {
        "topic": "spam",
        "event_id": eid,
        "timestamp": "2025-11-06T00:00:00Z",
        "source": "pytest",
        "payload": {"x": 1}
    }
    for _ in range(50):
        requests.post(f"{BASE}/publish", json=event)

    events = requests.get(f"{BASE}/events?topic=spam").json()
    assert len([e for e in events if e["event_id"] == eid]) == 1

