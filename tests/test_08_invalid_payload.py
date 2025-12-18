import requests, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_invalid_payload_type():
    event = {
        "topic": "bad",
        "event_id": "bad-1",
        "timestamp": "2025-11-06T00:00:00Z",
        "source": "pytest",
        "payload": "not-dict"
    }
    r = requests.post(f"{BASE}/publish", json=event)
    assert r.status_code in (400, 422)
