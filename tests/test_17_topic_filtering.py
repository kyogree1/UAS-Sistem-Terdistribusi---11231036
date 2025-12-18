import requests, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_topic_filtering():
    r = requests.get(f"{BASE}/events?topic=orders")
    assert r.status_code == 200
