from pathlib import Path
import unittest


HTML = Path(__file__).with_name("index.html").read_text(encoding="utf-8")


class ClientPortalSmokeTest(unittest.TestCase):
    def test_request_form_exists(self):
        self.assertIn("New Request Form", HTML)
        self.assertIn('id="submitRequestBtn"', HTML)
        self.assertIn('/projects/requests', HTML)

    def test_clarification_inbox_exists(self):
        self.assertIn("Clarification Inbox", HTML)
        self.assertIn('id="loadClarificationsBtn"', HTML)
        self.assertIn('/clarification/start', HTML)
        self.assertIn('/clarification/answers', HTML)

    def test_timeline_status_exists(self):
        self.assertIn("Project Timeline / Status", HTML)
        self.assertIn('id="projectRows"', HTML)
        self.assertIn("TIMELINE_STEPS", HTML)


if __name__ == "__main__":
    unittest.main()
