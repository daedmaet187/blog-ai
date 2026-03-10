from dataclasses import dataclass
import os
import re


@dataclass(slots=True)
class ProvisionedRepository:
    full_name: str
    html_url: str
    clone_url: str
    default_branch: str = "main"


class GitHubProvisioner:
    """Minimal GitHub repository provisioner abstraction.

    Network calls are intentionally omitted for Task 6; tests can monkeypatch
    `create_repository` to simulate GitHub API behavior.
    """

    def __init__(self, *, org: str | None = None, repo_prefix: str | None = None):
        self.org = org or os.getenv("GITHUB_OWNER", "daedmaet187")
        self.repo_prefix = (repo_prefix or os.getenv("GITHUB_REPO_PREFIX", "lp")).strip("-")

    @staticmethod
    def _slugify(value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return slug or "project"

    def create_repository(self, *, repo_name: str, description: str) -> dict[str, str]:
        return {
            "full_name": f"{self.org}/{repo_name}",
            "html_url": f"https://github.com/{self.org}/{repo_name}",
            "clone_url": f"https://github.com/{self.org}/{repo_name}.git",
            "default_branch": "main",
        }

    def provision_for_project(self, *, client_user_id: int, project_id: int, title: str) -> ProvisionedRepository:
        repo_name = f"{self.repo_prefix}-c{client_user_id}-p{project_id}-{self._slugify(title)}"
        payload = self.create_repository(
            repo_name=repo_name,
            description=f"Landing page project {project_id}: {title}",
        )
        return ProvisionedRepository(
            full_name=str(payload["full_name"]),
            html_url=str(payload["html_url"]),
            clone_url=str(payload["clone_url"]),
            default_branch=str(payload.get("default_branch", "main")),
        )
