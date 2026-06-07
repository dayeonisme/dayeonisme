from scripts.update_featured_projects import project_rows, replace_featured_projects


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
        "| [📌 new-tool](https://github.com/dayeonisme/new-tool) | New automation tool |",
        "| [🏠 private-project](https://github.com/dayeonisme/private-project) | Private project |",
    ]


def test_replace_featured_projects_only_updates_marked_section():
    readme = "before\n<!-- featured-projects:start -->\nold\n<!-- featured-projects:end -->\nafter"

    updated = replace_featured_projects(readme, ["new"])

    assert updated == "before\n<!-- featured-projects:start -->\nnew\n<!-- featured-projects:end -->\nafter"
