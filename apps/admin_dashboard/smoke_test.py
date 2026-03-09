from pathlib import Path
import unittest


HTML = Path(__file__).with_name("index.html").read_text(encoding="utf-8")


class AdminDashboardModerationSmokeTest(unittest.TestCase):
    def test_moderation_queue_section_is_present(self):
        self.assertIn("Moderation Queue", HTML)
        self.assertIn('id="modRows"', HTML)
        self.assertIn('id="modStatusFilter"', HTML)

    def test_override_actions_are_present(self):
        self.assertIn('data-mod-action="approve"', HTML)
        self.assertIn('data-mod-action="reject"', HTML)
        self.assertIn('/moderation/queue/${itemId}/override', HTML)

    def test_reason_codes_are_rendered_with_labels(self):
        for reason in [
            "BLOCKED_WORD",
            "TOO_MANY_LINKS",
            "DUPLICATE_CONTENT",
            "TOO_MANY_MEDIA",
        ]:
            self.assertIn(reason, HTML)
        self.assertIn("renderReasonChips", HTML)
        self.assertIn("reason-code", HTML)


if __name__ == "__main__":
    unittest.main()
