from scripts.update_featured_projects import project_rows, replace_featured_projects


def test_project_rows_include_public_non_profile_repos_sorted_by_name():
    repos = [
        {
            "name": "dayeonisme",
            "html_url": "https://github.com/dayeonisme/dayeonisme",
            "description": None,
            "private": False,
            "fork": False,
            "archived": False,
        },
        {
            "name": "private-project",
            "html_url": "https://github.com/dayeonisme/private-project",
            "description": None,
            "private": False,
            "fork": False,
            "archived": False,
        },
        {
            "name": "new-tool",
            "html_url": "https://github.com/dayeonisme/new-tool",
            "description": "New automation tool",
            "private": False,
            "fork": False,
            "archived": False,
        },
        {
            "name": "private-tool",
            "html_url": "https://github.com/dayeonisme/private-tool",
            "description": "Hidden",
            "private": True,
            "fork": False,
            "archived": False,
        },
    ]

    rows = project_rows(repos)

    assert rows == [
        "| Project | Description |",
        "|---|---|",
        "| [🏠 private-project](https://github.com/dayeonisme/private-project) | Private project |",
        "| [📌 new-tool](https://github.com/dayeonisme/new-tool) | New automation tool |",
    ]


def test_replace_featured_projects_only_updates_marked_section():
    readme = "before\n<!-- featured-projects:start -->\nold\n<!-- featured-projects:end -->\nafter"

    updated = replace_featured_projects(readme, ["new"])

    assert updated == "before\n<!-- featured-projects:start -->\nnew\n<!-- featured-projects:end -->\nafter"
