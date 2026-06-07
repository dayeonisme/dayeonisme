from scripts.update_featured_projects import project_emoji, project_rows, replace_featured_projects, replace_tech_stack, tech_stack_icons


def test_project_rows_include_public_non_profile_repos_sorted_by_created_at():
    repos = [
        {
            "name": "dayeonisme",
            "html_url": "https://github.com/dayeonisme/dayeonisme",
            "description": None,
            "private": False,
            "fork": False,
            "archived": False,
            "created_at": "2024-01-01T00:00:00Z",
        },
        {
            "name": "private-project",
            "html_url": "https://github.com/dayeonisme/private-project",
            "description": None,
            "private": False,
            "fork": False,
            "archived": False,
            "created_at": "2026-06-07T00:00:00Z",
        },
        {
            "name": "new-tool",
            "html_url": "https://github.com/dayeonisme/new-tool",
            "description": "New automation tool",
            "private": False,
            "fork": False,
            "archived": False,
            "created_at": "2023-01-01T00:00:00Z",
        },
        {
            "name": "private-tool",
            "html_url": "https://github.com/dayeonisme/private-tool",
            "description": "Hidden",
            "private": True,
            "fork": False,
            "archived": False,
            "created_at": "2022-01-01T00:00:00Z",
        },
    ]

    rows = project_rows(repos)

    assert rows == [
        "| Project | Description |",
        "|---|---|",
        "| [🤖 new-tool](https://github.com/dayeonisme/new-tool) | New automation tool |",
        "| [🏠 private-project](https://github.com/dayeonisme/private-project) | Private project |",
    ]


def test_project_emoji_infers_from_repo_content_without_explicit_mapping():
    assert (
        project_emoji(
            {
                "name": "movie-ratings",
                "description": "Watched movie diary with ratings and reviews",
                "topics": ["film", "review"],
            }
        )
        == "🎬"
    )
    assert (
        project_emoji(
            {
                "name": "budget-dashboard",
                "description": "Personal finance tracker",
                "topics": ["money"],
            }
        )
        == "💰"
    )
    assert (
        project_emoji(
            {
                "name": "unknown-project",
                "description": "",
                "topics": [],
            }
        )
        == "📌"
    )


def test_project_rows_avoid_duplicate_inferred_emojis_when_possible():
    repos = [
        {
            "name": "first-automation",
            "html_url": "https://github.com/dayeonisme/first-automation",
            "description": "Automation workflow tool",
            "private": False,
            "fork": False,
            "archived": False,
            "created_at": "2023-01-01T00:00:00Z",
        },
        {
            "name": "second-automation",
            "html_url": "https://github.com/dayeonisme/second-automation",
            "description": "Automation workflow tool",
            "private": False,
            "fork": False,
            "archived": False,
            "created_at": "2024-01-01T00:00:00Z",
        },
    ]

    rows = project_rows(repos)

    assert rows == [
        "| Project | Description |",
        "|---|---|",
        "| [🤖 first-automation](https://github.com/dayeonisme/first-automation) | Automation workflow tool |",
        "| [⚙️ second-automation](https://github.com/dayeonisme/second-automation) | Automation workflow tool |",
    ]


def test_replace_featured_projects_only_updates_marked_section():
    readme = "before\n<!-- featured-projects:start -->\nold\n<!-- featured-projects:end -->\nafter"

    updated = replace_featured_projects(readme, ["new"])

    assert updated == "before\n<!-- featured-projects:start -->\nnew\n<!-- featured-projects:end -->\nafter"


def test_tech_stack_icons_keep_core_stack_and_add_repo_languages():
    languages_by_repo = {
        "repo-a": {"Python": 1200, "TypeScript": 900, "Jupyter Notebook": 300},
        "repo-b": {"Go": 800, "HTML": 50},
        "repo-c": {"UnknownLang": 500},
    }

    icons = tech_stack_icons(languages_by_repo)

    assert icons[:10] == ["py", "sqlite", "flask", "fastapi", "docker", "js", "html", "css", "bash", "git"]
    assert "ts" in icons
    assert "go" in icons
    assert "jupyter" in icons
    assert "unknownlang" not in icons
    assert "git" in icons
    assert "github" not in icons
    assert "githubactions" not in icons


def test_replace_tech_stack_only_updates_marked_section():
    readme = "before\n<!-- tech-stack:start -->\nold\n<!-- tech-stack:end -->\nafter"

    updated = replace_tech_stack(readme, ["py", "go"])

    assert (
        updated
        == "before\n<!-- tech-stack:start -->\n[![Skillicons](https://skillicons.dev/icons?i=py,go)](https://skillicons.dev)\n<!-- tech-stack:end -->\nafter"
    )
