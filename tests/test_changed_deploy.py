from deploy import changed_deploy


def test_changed_files_working_tree_includes_untracked_deployables(monkeypatch):
    outputs = {
        ("diff", "--name-status", "origin/main"): "M\tapp/main.py\nD\tapp/old.py",
        ("ls-files", "--others", "--exclude-standard"): (
            "app/services/new_queue.py\n"
            "migrations/versions/new_queue.py\n"
            "client-portal/src/App.tsx"
        ),
    }
    monkeypatch.setattr(changed_deploy, "run_git", lambda args: outputs.get(tuple(args), ""))

    changes = changed_deploy.changed_files("origin/main", include_working_tree=True)

    assert ("M", "app/main.py") in changes
    assert ("D", "app/old.py") in changes
    assert ("A", "app/services/new_queue.py") in changes
    assert ("A", "migrations/versions/new_queue.py") in changes
    assert all(path != "client-portal/src/App.tsx" for _, path in changes)


def test_local_deployable_changes_reports_omitted_dirty_paths(monkeypatch):
    outputs = {
        ("diff", "--name-only"): "app/routers/admin_api.py\nREADME.md",
        ("diff", "--cached", "--name-only"): "requirements.txt",
        ("ls-files", "--others", "--exclude-standard"): (
            "app/static/client-portal/assets/new.js\n"
            "client-portal/src/App.tsx"
        ),
    }
    monkeypatch.setattr(changed_deploy, "run_git", lambda args: outputs.get(tuple(args), ""))

    assert changed_deploy.local_deployable_changes() == [
        "app/routers/admin_api.py",
        "app/static/client-portal/assets/new.js",
        "requirements.txt",
    ]
