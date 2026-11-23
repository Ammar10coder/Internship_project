import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from fastapi.testclient import TestClient
from backend.api import create_app
from backend.scoring import classify

ROOT = Path(__file__).resolve().parents[1]


class TenderWorkflow(unittest.TestCase):
    def test_rules(self):
        cases = [
            ("Construction of Boundary Wall and Gate", 87, "P0"),
            ("Construction of Two class rooms for School", 73, "P2"),
            ("Road repair with concrete resurfacing", 80, "P1"),
            ("Boundary wall with catering", 20, "—"),
            ("Office stationery", 30, "—"),
        ]
        for text, score, priority in cases:
            with self.subTest(text=text):
                result = classify(text)
                self.assertEqual((result.score, result.priority), (score, priority))

    def test_presentation(self):
        with TemporaryDirectory() as directory:
            database = Path(directory) / "demo.db"
            with TestClient(create_app(database)) as client:
                for route in ("/", "/style.css", "/app.js"):
                    self.assertEqual(client.get(route).status_code, 200)
                pdf = (ROOT / "samples" / "Boundary-wall.pdf").read_bytes()
                result = client.post("/api/extract", files={"file": ("sample.pdf", pdf)})
                self.assertEqual(result.status_code, 200)
                res = client.post("/api/tenders", json={"title":"Campus gate", "description":result.json()["text"]})
                self.assertEqual(res.status_code, 201)
                self.assertEqual(res.json()["score"], 87)
                self.assertEqual(client.post("/api/extract", files={"file":("broken.pdf",b"oops")}).status_code, 422)
                self.assertEqual(client.post("/api/tenders", json={"title":" ", "description":"abc"}).status_code, 422)
            with TestClient(create_app(database)) as client:
                self.assertEqual(client.get("/api/tenders?decision=GO").json()[0]["title"], "Campus gate")
                self.assertEqual(client.get("/api/tenders?decision=NO-GO").json(), [])
