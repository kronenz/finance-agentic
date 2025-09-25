"""
API security testing and validation.
"""
import unittest
from fastapi.testclient import TestClient

from app.main import app

class TestAPISecurity(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_missing_api_key(self):
        """Test for missing API key."""
        response = self.client.get("/api/v1/data")
        self.assertEqual(response.status_code, 403)

    def test_invalid_api_key(self):
        """Test for invalid API key."""
        response = self.client.get("/api/v1/data", headers={"X-API-Key": "invalid"})
        self.assertEqual(response.status_code, 403)
