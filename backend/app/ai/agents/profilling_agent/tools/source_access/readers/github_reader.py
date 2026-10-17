from urllib.parse import urlparse

import requests

from app.core.config import settings


class GitHubReader:

    API_BASE_URL = "https://api.github.com"

    TEXT_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".md",
        ".txt",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".sql",
        ".html",
        ".css",
        ".sh",
    }

    IMPORTANT_FILENAMES = {
        "README",
        "README.md",
        "requirements.txt",
        "pyproject.toml",
        "package.json",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
    }

    def __init__(
        self,
        token: str | None = None,
    ):
        self.token = token or settings.GITHUB_TOKEN

    def read(
        self,
        repo_url: str,
    ) -> str:

        owner, repo = self._parse_repo_url(repo_url)

        repo_data = self._get_repository(
            owner=owner,
            repo=repo,
        )

        default_branch = repo_data["default_branch"]

        tree = self._get_repository_tree(
            owner=owner,
            repo=repo,
            branch=default_branch,
        )

        selected_files = self._select_files(tree)

        parts: list[str] = []

        parts.append(
            f"[Repository: {owner}/{repo}]"
        )

        if repo_data.get("description"):
            parts.append(
                f"Description: {repo_data['description']}"
            )

        parts.append(
            f"Default branch: {default_branch}"
        )

        parts.append("\n[Repository Structure]")

        for file_path in selected_files:
            parts.append(file_path)

        parts.append("\n[Repository Contents]")

        for file_path in selected_files:

            try:
                content = self._read_file(
                    owner=owner,
                    repo=repo,
                    file_path=file_path,
                    branch=default_branch,
                )

            except Exception as error:
                parts.append(
                    f"\n[File: {file_path}]"
                    f"\nCould not read file: {error}"
                )
                continue

            parts.append(
                f"\n[File: {file_path}]\n{content}"
            )

        return "\n".join(parts)

    def _parse_repo_url(
        self,
        repo_url: str,
    ) -> tuple[str, str]:

        parsed = urlparse(repo_url)

        if parsed.hostname != "github.com":
            raise ValueError(
                "URL is not a GitHub repository URL."
            )

        path_parts = [
            part
            for part in parsed.path.split("/")
            if part
        ]

        if len(path_parts) < 2:
            raise ValueError(
                "Invalid GitHub repository URL."
            )

        owner = path_parts[0]
        repo = path_parts[1]

        if repo.endswith(".git"):
            repo = repo[:-4]

        return owner, repo

    def _headers(self) -> dict[str, str]:

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        if self.token:
            headers["Authorization"] = (
                f"Bearer {self.token}"
            )

        return headers

    def _get_repository(
        self,
        owner: str,
        repo: str,
    ) -> dict:

        url = (
            f"{self.API_BASE_URL}"
            f"/repos/{owner}/{repo}"
        )

        response = requests.get(
            url,
            headers=self._headers(),
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def _get_repository_tree(
        self,
        owner: str,
        repo: str,
        branch: str,
    ) -> list[dict]:

        url = (
            f"{self.API_BASE_URL}"
            f"/repos/{owner}/{repo}"
            f"/git/trees/{branch}"
        )

        response = requests.get(
            url,
            headers=self._headers(),
            params={
                "recursive": "1",
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("tree", [])

    def _select_files(
        self,
        tree: list[dict],
    ) -> list[str]:

        selected: list[str] = []

        for item in tree:

            if item.get("type") != "blob":
                continue

            path = item.get("path")

            if not path:
                continue

            filename = path.split("/")[-1]

            if filename in self.IMPORTANT_FILENAMES:
                selected.append(path)
                continue

            for extension in self.TEXT_EXTENSIONS:
                if filename.lower().endswith(extension):
                    selected.append(path)
                    break

        return selected

    def _read_file(
        self,
        owner: str,
        repo: str,
        file_path: str,
        branch: str,
    ) -> str:

        url = (
            f"{self.API_BASE_URL}"
            f"/repos/{owner}/{repo}"
            f"/contents/{file_path}"
        )

        headers = self._headers()
        headers["Accept"] = "application/vnd.github.raw+json"

        response = requests.get(
            url,
            headers=headers,
            params={
                "ref": branch,
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.text