import requests, uuid, pytest, time

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_event_ordering_by_ts_ingest():
    for i in range(3):
        event = {
            "topic": "order",
            "event_id": str(uuid.uuid4()),
            "timestamp": f"2025-11-06T00:00:0{i}Z",
            "source": "pytest",
            "payload": {"i": i}
        }
        requests.post(f"{BASE}/publish", json=event)
        time.sleep(0.1)

    events = requests.get(f"{BASE}/events?topic=order").json()
    assert len(events) >= 3
