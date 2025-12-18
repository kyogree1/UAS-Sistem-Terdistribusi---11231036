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
('received',0),('unique_processed',0),('duplicate_dropped',0)
ON CONFLICT DO NOTHING;
