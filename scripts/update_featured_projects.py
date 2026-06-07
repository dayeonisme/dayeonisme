from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


OWNER = "dayeonisme"
README = Path("README.md")
START = "<!-- featured-projects:start -->"
END = "<!-- featured-projects:end -->"
EXCLUDED_REPOS = {"dayeonisme"}

EMOJI_BY_REPO = {
    "personal-finance": "💰",
    "navermap-converter": "🗺",
    "personal-cinelog": "🎬",
    "private-project": "🏠",
    "lottery-pension-auto": "🎱",
    "pagewatch-ping": "🔔",
}

DESCRIPTION_OVERRIDES = {
    "personal-finance": "Personal finance tracker & dashboard",
    "navermap-converter": "Naver Map data converter",
    "personal-cinelog": "Personal cinema log",
    "private-project": "Private project",
    "lottery-pension-auto": "Lotto 6/45 & Pension auto-buy & report",
}


def fetch_public_repos(owner: str = OWNER) -> list[dict[str, Any]]:
    token = os.environ.get("GITHUB_TOKEN", "")
    request = Request(
        f"https://api.github.com/users/{owner}/repos?type=owner&sort=updated&per_page=100",
        headers={
            "Accept": "application/vnd.github+json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def description_for(repo: dict[str, Any]) -> str:
    name = repo["name"]
    if name in DESCRIPTION_OVERRIDES:
        return DESCRIPTION_OVERRIDES[name]
    return repo.get("description") or name.replace("-", " ").title()


def project_rows(repos: list[dict[str, Any]]) -> list[str]:
    public_repos = [
        repo
        for repo in repos
        if not repo.get("private")
        and not repo.get("fork")
        and not repo.get("archived")
        and repo["name"] not in EXCLUDED_REPOS
    ]
    public_repos.sort(key=lambda repo: repo["name"].lower())
    rows = ["| Project | Description |", "|---|---|"]
    for repo in public_repos:
        name = repo["name"]
        emoji = EMOJI_BY_REPO.get(name, "📌")
        rows.append(f"| [{emoji} {name}]({repo['html_url']}) | {description_for(repo)} |")
    return rows


def replace_featured_projects(readme: str, rows: list[str]) -> str:
    before, rest = readme.split(START, 1)
    _, after = rest.split(END, 1)
    body = "\n".join([START, *rows, END])
    return before + body + after


def main() -> None:
    readme = README.read_text(encoding="utf-8")
    updated = replace_featured_projects(readme, project_rows(fetch_public_repos()))
    README.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
