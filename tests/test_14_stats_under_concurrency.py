import requests, uuid, concurrent.futures, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_stats_under_concurrency():
    def send():
        return requests.post(f"{BASE}/publish", json={
            "topic": "load",
            "event_id": str(uuid.uuid4()),
            "timestamp": "2025-11-06T00:00:00Z",
            "source": "pytest",
            "payload": {"x": 1}
        }).status_code

    with concurrent.futures.ThreadPoolExecutor(20) as ex:
        results = list(ex.map(lambda _: send(), range(20)))

    assert all(r == 200 for r in results)
