"""
Security vulnerability scanning and auditing.
"""
import unittest
import subprocess

class TestVulnerabilities(unittest.TestCase):

    def test_bandit_scan(self):
        """Run Bandit to scan for common security issues."""
        try:
            result = subprocess.run(
                ["bandit_env/bin/bandit", "-r", "backend/app"],
                capture_output=True,
                text=True,
                check=True
            )
            # If bandit finds issues, it will print them to stdout and exit with a non-zero code.
            # The check=True argument will cause a CalledProcessError to be raised if the exit code is non-zero.
            # We can then assert that the return code is 0, which means no issues were found.
            self.assertEqual(result.returncode, 0, f"Bandit found security vulnerabilities:\n{result.stdout}")
        except FileNotFoundError:
            self.fail("Bandit is not installed. Please install it with 'pip install bandit'")
        except subprocess.CalledProcessError as e:
            self.fail(f"Bandit found security vulnerabilities:\n{e.stdout}")