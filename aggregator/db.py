import asyncpg
import os
import asyncio

DB_URL = os.getenv("DATABASE_URL")

async def init_db(retries: int = 10, delay: int = 2):
    last_error = None
    for i in range(retries):
        try:
            pool = await asyncpg.create_pool(dsn=DB_URL)
            async with pool.acquire() as conn:
                await conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_events (
                    topic TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    ts_ingest TIMESTAMPTZ DEFAULT now(),
                    source TEXT,
                    payload JSONB NOT NULL,
                    PRIMARY KEY (topic, event_id)
                );

                CREATE TABLE IF NOT EXISTS stats (
                    key TEXT PRIMARY KEY,
                    val BIGINT NOT NULL
                );

                INSERT INTO stats(key,val) VALUES
                    ('received',0),
                    ('unique_processed',0),
                    ('duplicate_dropped',0)
                ON CONFLICT DO NOTHING;
                """)
            print("✅ Database connected & initialized")
            return pool
        except Exception as e:
            last_error = e
            print(f"⏳ Waiting for database... ({i+1}/{retries})")
            await asyncio.sleep(delay)

    raise RuntimeError(f"❌ Database not ready after retries: {last_error}")