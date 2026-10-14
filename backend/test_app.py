"""Unit tests for the HealthTracker API (Jira HA-17)."""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from app import HealthTrackerHandler, initialize_db


class HealthTrackerApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.db_path = str(Path(cls.tempdir.name) / "test-healthtracker.db")
        initialize_db(cls.db_path)
        HealthTrackerHandler.db_path = cls.db_path
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), HealthTrackerHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:%s" % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.tempdir.cleanup()

    def request(self, path, method="GET", payload=None):
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.base + path, data=data, method=method)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            response = urllib.request.urlopen(req)
            return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))

    def test_health_endpoint(self):
        status, body = self.request("/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_create_and_persist_record(self):
        record = {"user_id": "demo-user", "metric": "steps", "value": 6240, "recorded_at": "2026-10-15"}
        status, created = self.request("/records", "POST", record)
        self.assertEqual(status, 201)
        status, body = self.request("/records")
        self.assertEqual(status, 200)
        self.assertTrue(any(row["id"] == created["id"] for row in body["records"]))

    def test_reject_invalid_value(self):
        status, body = self.request("/records", "POST", {
            "user_id": "demo-user", "metric": "steps", "value": "many", "recorded_at": "2026-10-15"
        })
        self.assertEqual(status, 400)
        self.assertIn("numeric", body["error"])

    def test_unknown_route(self):
        status, body = self.request("/not-found")
        self.assertEqual(status, 404)
        self.assertIn("error", body)


if __name__ == "__main__":
    unittest.main()
