-- HealthTracker MVP health record storage (HA-16)
-- SQLite schema used by backend/app.py. Demo data only; do not store real personal health information here.
CREATE TABLE IF NOT EXISTS health_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL CHECK (length(trim(user_id)) > 0),
    metric TEXT NOT NULL CHECK (length(trim(metric)) > 0),
    value REAL NOT NULL CHECK (value > -1000000000 AND value < 1000000000),
    recorded_at TEXT NOT NULL CHECK (length(trim(recorded_at)) > 0)
);

CREATE INDEX IF NOT EXISTS idx_health_records_user_recorded
    ON health_records (user_id, recorded_at);
