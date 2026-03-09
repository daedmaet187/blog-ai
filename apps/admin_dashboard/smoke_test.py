from pathlib import Path
import unittest


HTML = Path(__file__).with_name("index.html").read_text(encoding="utf-8")


class AdminDashboardApprovalSmokeTest(unittest.TestCase):
    def test_approval_queue_section_is_present(self):
        self.assertIn("Approval Queue", HTML)
        self.assertIn('id="queueRows"', HTML)
        self.assertIn('/admin/projects/approval-queue', HTML)

    def test_design_and_deploy_actions_are_present(self):
        self.assertIn('data-action="design-approve"', HTML)
        self.assertIn('data-action="design-reject"', HTML)
        self.assertIn('data-action="deploy-approve"', HTML)
        self.assertIn('data-action="deploy-reject"', HTML)


if __name__ == "__main__":
    unittest.main()
