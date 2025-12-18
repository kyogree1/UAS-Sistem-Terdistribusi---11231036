CREATE TABLE IF NOT EXISTS events_ingested (
  id SERIAL PRIMARY KEY,
  topic TEXT NOT NULL,
  event_id TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  source TEXT NOT NULL,
  payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS processed_events (
  id SERIAL PRIMARY KEY,
  topic TEXT NOT NULL,
  event_id TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  source TEXT NOT NULL,
  payload JSONB NOT NULL,
  UNIQUE (topic, event_id)
);

CREATE TABLE IF NOT EXISTS outbox (
  id SERIAL PRIMARY KEY,
  topic TEXT NOT NULL,
  event_id TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  source TEXT NOT NULL,
  payload JSONB NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  attempts INT NOT NULL DEFAULT 0
);
