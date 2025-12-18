import requests, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_event_list_not_empty():
    r = requests.get(f"{BASE}/events")
    assert isinstance(r.json(), list)
