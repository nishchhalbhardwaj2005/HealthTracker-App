"""Minimal HealthTracker JSON API with SQLite persistence (Jira HA-17)."""
import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DB_PATH = os.environ.get("HEALTHTRACKER_DB", "healthtracker.db")


def connect_db(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db(path=DB_PATH):
    with connect_db(path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                recorded_at TEXT NOT NULL
            )
        """)


class HealthTrackerHandler(BaseHTTPRequestHandler):
    db_path = DB_PATH

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 65536:
                return None
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            return None

    def do_GET(self):
        if self.path == "/health":
            return self._send_json(200, {"status": "ok", "service": "HealthTracker API"})
        if self.path == "/records":
            with connect_db(self.db_path) as conn:
                rows = conn.execute(
                    "SELECT id, user_id, metric, value, recorded_at FROM health_records ORDER BY id"
                ).fetchall()
            return self._send_json(200, {"records": [dict(row) for row in rows]})
        return self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        if self.path != "/records":
            return self._send_json(404, {"error": "Endpoint not found"})
        data = self._read_json()
        if not isinstance(data, dict):
            return self._send_json(400, {"error": "Request body must be valid JSON"})
        user_id = data.get("user_id")
        metric = data.get("metric")
        value = data.get("value")
        recorded_at = data.get("recorded_at")
        if not all(isinstance(v, str) and v.strip() for v in (user_id, metric, recorded_at)):
            return self._send_json(400, {"error": "user_id, metric and recorded_at are required"})
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return self._send_json(400, {"error": "value must be numeric"})
        if not (-1e9 < float(value) < 1e9):
            return self._send_json(400, {"error": "value is outside the supported range"})
        with connect_db(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO health_records (user_id, metric, value, recorded_at) VALUES (?, ?, ?, ?)",
                (user_id.strip(), metric.strip(), float(value), recorded_at.strip())
            )
            record_id = cursor.lastrowid
        return self._send_json(201, {
            "id": record_id, "user_id": user_id.strip(), "metric": metric.strip(),
            "value": float(value), "recorded_at": recorded_at.strip()
        })

    def log_message(self, *_args):
        pass


def main():
    initialize_db(DB_PATH)
    server = ThreadingHTTPServer(("127.0.0.1", 8000), HealthTrackerHandler)
    print("HealthTracker API listening on http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
