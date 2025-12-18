import requests, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_invalid_schema_rejected():
    invalid = {"topic": "x", "payload": {"a": 1}}
    r = requests.post(f"{BASE}/publish", json=invalid)
    assert r.status_code in (400, 422)
