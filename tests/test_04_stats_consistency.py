import requests, uuid, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_stats_consistency_balance():
    eid = str(uuid.uuid4())
    event = {
        "topic": "stats",
        "event_id": eid,
        "timestamp": "2025-11-06T00:00:00Z",
        "source": "pytest",
        "payload": {"x": 1}
    }
    requests.post(f"{BASE}/publish", json=event)
    requests.post(f"{BASE}/publish", json=event)

    stats = requests.get(f"{BASE}/stats").json()
    assert stats["received"] >= 2
    assert stats["unique_processed"] >= 1
    assert stats["duplicate_dropped"] >= 1
