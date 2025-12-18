import requests, uuid, pytest, time

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_data_persistent_across_container_restart():
    eid = str(uuid.uuid4())
    event = {
        "topic": "persist",
        "event_id": eid,
        "timestamp": "2025-11-06T00:00:00Z",
        "source": "pytest",
        "payload": {"msg": "persist"}
    }
    r = requests.post(f"{BASE}/publish", json=event)
    assert r.status_code == 200

    time.sleep(1)  # assume container restarted manually

    events = requests.get(f"{BASE}/events?topic=persist").json()
    assert any(e["event_id"] == eid for e in events)
