import requests, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_stats_endpoint_stable():
    r1 = requests.get(f"{BASE}/stats").json()
    r2 = requests.get(f"{BASE}/stats").json()
    assert r1.keys() == r2.keys()
