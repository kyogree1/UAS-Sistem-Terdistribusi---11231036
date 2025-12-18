import requests, pytest

BASE = "http://localhost:8080"

@pytest.mark.asyncio
async def test_stats_keys_exist():
    stats = requests.get(f"{BASE}/stats").json()
    for k in ("received", "unique_processed", "duplicate_dropped"):
        assert k in stats   