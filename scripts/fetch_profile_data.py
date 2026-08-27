#!/usr/bin/env python3
"""Fetch public GitHub profile data for the Systems Intelligence Lab renderer."""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "profile.config.json"
OUT_PATH = ROOT / "data" / "profile.json"


def get_json(url: str) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "HazaVVIP-profile-renderer/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    username = config["username"]
    user = get_json(f"https://api.github.com/users/{urllib.parse.quote(username)}")
    repositories = get_json(
        f"https://api.github.com/users/{urllib.parse.quote(username)}/repos?per_page=100&sort=updated"
    )
    if not isinstance(user, dict) or not isinstance(repositories, list):
        raise RuntimeError("Unexpected GitHub API response")

    domain_by_repo: dict[str, str] = {}
    for domain in config.get("domains", []):
        for repo_name in domain.get("repositories", []):
            domain_by_repo[repo_name.lower()] = domain["label"]

    cleaned_repositories: list[dict[str, object]] = []
    for repo in repositories:
        if not isinstance(repo, dict) or repo.get("fork"):
            continue
        name = str(repo.get("name", ""))
        cleaned_repositories.append(
            {
                "name": name,
                "description": repo.get("description") or "public engineering artifact",
                "language": repo.get("language") or "Other",
                "stars": int(repo.get("stargazers_count") or 0),
                "forks": int(repo.get("forks_count") or 0),
                "domain": domain_by_repo.get(name.lower(), "EXPERIMENTS"),
                "updated_at": repo.get("updated_at"),
            }
        )

    payload = {
        "username": username,
        "name": user.get("name") or username,
        "followers": int(user.get("followers") or 0),
        "following": int(user.get("following") or 0),
        "public_repos": int(user.get("public_repos") or len(cleaned_repositories)),
        "public_gists": int(user.get("public_gists") or 0),
        "updated_at": user.get("updated_at"),
        "repositories": cleaned_repositories,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(cleaned_repositories)} public repositories to {OUT_PATH}")


if __name__ == "__main__":
    main()
