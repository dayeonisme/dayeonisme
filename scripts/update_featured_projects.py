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
TECH_STACK_START = "<!-- tech-stack:start -->"
TECH_STACK_END = "<!-- tech-stack:end -->"
EXCLUDED_REPOS = {"dayeonisme"}
EXCLUDED_TECH_STACK = {"github", "githubactions"}
CORE_TECH_STACK = ["py", "sqlite", "flask", "fastapi", "docker", "js", "html", "css", "bash", "git"]

LANGUAGE_TO_SKILLICON = {
    "Python": "py",
    "JavaScript": "js",
    "TypeScript": "ts",
    "HTML": "html",
    "CSS": "css",
    "Shell": "bash",
    "Dockerfile": "docker",
    "Go": "go",
    "Java": "java",
    "Kotlin": "kotlin",
    "Swift": "swift",
    "Rust": "rust",
    "Ruby": "ruby",
    "PHP": "php",
    "C": "c",
    "C++": "cpp",
    "C#": "cs",
    "R": "r",
    "Jupyter Notebook": "jupyter",
}

EMOJI_BY_REPO = {
    "personal-finance": "💰",
    "navermap-converter": "🗺",
    "personal-cinelog": "🎬",
    "private-project": "🏠",
    "lottery-pension-auto": "🎱",
    "pagewatch-ping": "🔔",
}

EMOJI_RULES = [
    ("💰", {"finance", "money", "budget", "expense", "income", "asset", "portfolio"}),
    ("🗺", {"map", "naver", "location", "geo", "converter"}),
    ("🎬", {"movie", "cinema", "film", "rating", "ratings", "review", "watched"}),
    ("🏠", {"home", "housing", "private-project", "subscription", "lh", "real-estate", "apartment"}),
    ("🎱", {"lottery", "lotto", "pension", "raffle"}),
    ("🔔", {"alert", "alerts", "watch", "watcher", "monitor", "notification", "telegram", "ping"}),
    ("📊", {"dashboard", "analytics", "analysis", "visualization", "report", "data"}),
    ("🤖", {"automation", "auto", "bot", "agent", "workflow", "tool"}),
    ("🌐", {"web", "site", "frontend", "html", "css"}),
]

DESCRIPTION_OVERRIDES = {
    "personal-finance": "Personal finance tracker & dashboard",
    "navermap-converter": "Naver Map data converter",
    "personal-cinelog": "Watched movie diary with ratings and reviews",
    "private-project": "Private project",
    "lottery-pension-auto": "Lotto 6/45 & Pension auto-buy & report",
}


def fetch_public_repos(owner: str = OWNER) -> list[dict[str, Any]]:
    token = os.environ.get("GITHUB_TOKEN", "")
    request = Request(
        f"https://api.github.com/users/{owner}/repos?type=owner&sort=created&direction=asc&per_page=100",
        headers={
            "Accept": "application/vnd.github+json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_repo_languages(repo: dict[str, Any]) -> dict[str, int]:
    token = os.environ.get("GITHUB_TOKEN", "")
    request = Request(
        repo["languages_url"],
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


def project_emoji(repo: dict[str, Any]) -> str:
    name = repo["name"]
    if name in EMOJI_BY_REPO:
        return EMOJI_BY_REPO[name]
    topics = repo.get("topics") or []
    searchable = " ".join([name, repo.get("description") or "", *topics]).lower()
    tokens = set(searchable.replace("_", "-").replace("/", "-").replace("&", " ").split())
    for emoji, keywords in EMOJI_RULES:
        if any(keyword in searchable or keyword in tokens for keyword in keywords):
            return emoji
    return "📌"


def project_rows(repos: list[dict[str, Any]]) -> list[str]:
    public_repos = public_feature_repos(repos)
    public_repos.sort(key=lambda repo: (repo.get("created_at") or "", repo["name"].lower()))
    rows = ["| Project | Description |", "|---|---|"]
    for repo in public_repos:
        name = repo["name"]
        emoji = project_emoji(repo)
        rows.append(f"| [{emoji} {name}]({repo['html_url']}) | {description_for(repo)} |")
    return rows


def public_feature_repos(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        repo
        for repo in repos
        if not repo.get("private")
        and not repo.get("fork")
        and not repo.get("archived")
        and repo["name"] not in EXCLUDED_REPOS
    ]


def tech_stack_icons(languages_by_repo: dict[str, dict[str, int]]) -> list[str]:
    icons = [icon for icon in CORE_TECH_STACK if icon not in EXCLUDED_TECH_STACK]
    seen = set(icons)
    languages = sorted(
        {
            language
            for repo_languages in languages_by_repo.values()
            for language, bytes_count in repo_languages.items()
            if bytes_count > 0
        }
    )
    for language in languages:
        icon = LANGUAGE_TO_SKILLICON.get(language)
        if icon and icon not in seen and icon not in EXCLUDED_TECH_STACK:
            seen.add(icon)
            icons.append(icon)
    return icons


def replace_featured_projects(readme: str, rows: list[str]) -> str:
    before, rest = readme.split(START, 1)
    _, after = rest.split(END, 1)
    body = "\n".join([START, *rows, END])
    return before + body + after


def replace_tech_stack(readme: str, icons: list[str]) -> str:
    before, rest = readme.split(TECH_STACK_START, 1)
    _, after = rest.split(TECH_STACK_END, 1)
    badge = f"[![Skillicons](https://skillicons.dev/icons?i={','.join(icons)})](https://skillicons.dev)"
    body = "\n".join([TECH_STACK_START, badge, TECH_STACK_END])
    return before + body + after


def main() -> None:
    repos = fetch_public_repos()
    feature_repos = public_feature_repos(repos)
    languages_by_repo = {
        repo["name"]: fetch_repo_languages(repo)
        for repo in feature_repos
        if repo.get("languages_url")
    }
    readme = README.read_text(encoding="utf-8")
    updated = replace_tech_stack(readme, tech_stack_icons(languages_by_repo))
    updated = replace_featured_projects(updated, project_rows(repos))
    README.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
