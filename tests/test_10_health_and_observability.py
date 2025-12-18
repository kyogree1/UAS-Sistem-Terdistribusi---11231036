import requests, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_health_and_stats_available():
    r = requests.get(f"{BASE}/stats")
    assert r.status_code == 200
