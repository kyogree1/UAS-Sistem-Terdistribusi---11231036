import requests, uuid, concurrent.futures, pytest

BASE = "http://localhost:8080"

def send(eid):
    event = {
        "topic": "concurrent",
        "event_id": eid,
        "timestamp": "2025-11-06T00:00:00Z",
        "source": "pytest",
        "payload": {"x": 1}
    }
    return requests.post(f"{BASE}/publish", json=event).status_code

@pytest.mark.asyncio
async def test_concurrent_upsert_atomicity():
    eid = str(uuid.uuid4())
    with concurrent.futures.ThreadPoolExecutor(10) as ex:
        results = list(ex.map(send, [eid]*10))
    assert all(r == 200 for r in results)
