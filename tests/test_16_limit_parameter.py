import requests, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_limit_parameter():
    r = requests.get(f"{BASE}/events?limit=1")
    assert r.status_code == 200
    assert len(r.json()) <= 1
