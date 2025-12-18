from fastapi import FastAPI, Request, HTTPException
from db import init_db
from datetime import datetime
import json   # <<< WAJIB

app = FastAPI(title="PubSub Log Aggregator")
DB_POOL = None


@app.on_event("startup")
async def startup():
    global DB_POOL
    DB_POOL = await init_db()


def validate_event(e: dict):
    if not isinstance(e, dict):
        raise HTTPException(status_code=400)

    required = {"topic", "event_id", "timestamp", "source", "payload"}
    if not required.issubset(e.keys()):
        raise HTTPException(status_code=400)

    if not isinstance(e["payload"], dict):
        raise HTTPException(status_code=400)


@app.post("/publish")
async def publish(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400)

    events = body["events"] if isinstance(body, dict) and "events" in body else [body]

    async with DB_POOL.acquire() as conn:
        async with conn.transaction():
            for e in events:
                validate_event(e)

                # stats: received
                await conn.execute(
                    "UPDATE stats SET val = val + 1 WHERE key = 'received'"
                )

                result = await conn.execute(
                    """
                    INSERT INTO processed_events(topic, event_id, ts_ingest, source, payload)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (topic, event_id) DO NOTHING
                    """,
                    e["topic"],
                    e["event_id"],
                    datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")),
                    e["source"],
                    json.dumps(e["payload"])  # <<< INI KUNCI FIX
                )

                if result == "INSERT 0 1":
                    await conn.execute(
                        "UPDATE stats SET val = val + 1 WHERE key = 'unique_processed'"
                    )
                else:
                    await conn.execute(
                        "UPDATE stats SET val = val + 1 WHERE key = 'duplicate_dropped'"
                    )

    return {"accepted": len(events)}


@app.get("/events")
async def list_events(topic: str | None = None, limit: int = 100):
    q = "SELECT topic,event_id,ts_ingest,source,payload FROM processed_events"
    args = []

    if topic:
        q += " WHERE topic=$1 ORDER BY ts_ingest DESC LIMIT $2"
        args = [topic, limit]
    else:
        q += " ORDER BY ts_ingest DESC LIMIT $1"
        args = [limit]

    async with DB_POOL.acquire() as conn:
        rows = await conn.fetch(q, *args)

    return [dict(r) for r in rows]


@app.get("/stats")
async def get_stats():
    async with DB_POOL.acquire() as conn:
        rows = await conn.fetch("SELECT key,val FROM stats")
    return {r["key"]: r["val"] for r in rows}
