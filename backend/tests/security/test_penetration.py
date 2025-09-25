"""
Penetration testing scenarios.
"""
import unittest
from fastapi.testclient import TestClient

from app.main import app

class TestPenetration(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities."""
        payloads = [
            "' OR 1=1 -- ",
            '" OR 1=1 -- ',
            "admin'--",
            "admin' #",
            "admin'/*",
            "' OR '1'='1' -- ",
            "' OR '1'='1' #",
            "' OR '1'='1'/*",
            "' OR 1=1 AND '1'='1",
            "' OR 1=1 AND 'a'='a",
        ]
        for payload in payloads:
            response = self.client.get(f"/users?username={payload}")
            self.assertNotEqual(response.status_code, 200, f"SQL Injection vulnerability found with payload: {payload}")

    def test_xss(self):
        """Test for XSS vulnerabilities."""
        payloads = [
            "<script>alert('XSS')</script>",
            '<img src="x" onerror="alert(\'XSS\')">',
            '<svg/onload=alert("XSS")>',
            '<iframe src="javascript:alert(`XSS`)"></iframe>',
        ]
        for payload in payloads:
            response = self.client.get(f"/search?query={payload}")
            self.assertNotIn("<script>", response.text, f"XSS vulnerability found with payload: {payload}")

    def test_command_injection(self):
        """Test for command injection vulnerabilities."""
        payloads = [
            "; ls -la",
            "| ls -la",
            "&& ls -la",
        ]
        for payload in payloads:
            response = self.client.post("/execute", json={"command": f"echo {payload}"})
            self.assertNotIn("total", response.text, f"Command injection vulnerability found with payload: {payload}")

    def test_auth_bypass(self):
        """Test for authentication bypass."""
        response = self.client.get("/admin/dashboard", allow_redirects=False)
        self.assertNotEqual(response.status_code, 200, "Authentication bypass vulnerability found")