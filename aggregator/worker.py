import asyncio, os, json, aioredis, asyncpg, logging
from db import init_db

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")

REDIS_URL = os.getenv("BROKER_URL", "redis://broker:6379")
QUEUE_KEY = os.getenv("QUEUE_KEY", "events_queue")

async def worker_task(name: str):
    pool = await init_db()
    redis = await aioredis.from_url(REDIS_URL)
    logging.info(f"[{name}] Worker started. Waiting...")
    while True:
        _, raw = await redis.blpop(QUEUE_KEY)
        try:
            event = json.loads(raw)
            async with pool.acquire() as conn:
                tx = conn.transaction()
                await tx.start()
                await conn.execute("UPDATE stats SET val=val+1 WHERE key='received'")
                result = await conn.execute("""
                    INSERT INTO processed_events(topic,event_id,source,payload)
                    VALUES($1,$2,$3,$4)
                    ON CONFLICT (topic,event_id) DO NOTHING
                """, event["topic"], event["event_id"], event.get("source"), json.dumps(event["payload"]))
                if result == "INSERT 0 1":
                    await conn.execute("UPDATE stats SET val=val+1 WHERE key='unique_processed'")
                    logging.info(f"[{name}] New event {event['event_id']}")
                else:
                    await conn.execute("UPDATE stats SET val=val+1 WHERE key='duplicate_dropped'")
                    logging.info(f"[{name}] Duplicate skipped {event['event_id']}")
                await tx.commit()
        except Exception as e:
            logging.error(f"[{name}] Error: {e}")

if __name__ == "__main__":
    workers = int(os.getenv("WORKERS", "2"))
    asyncio.run(asyncio.gather(*(worker_task(f"worker-{i+1}") for i in range(workers))))
