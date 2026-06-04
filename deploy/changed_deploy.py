"""Deploy only changed tracked files to the DigitalOcean app server.

Usage:
    set DO_SSH_PASSWORD=...
    python deploy/changed_deploy.py --base origin/main
    python deploy/changed_deploy.py --base origin/main --working-tree
    python deploy/changed_deploy.py --base origin/main --dry-run

Environment:
    DO_SSH_HOST       SSH host; required for non-dry-run deploys
    DO_SSH_USER       SSH user; required for non-dry-run deploys
    DO_SSH_PASSWORD   Optional SSH password; omit to use local SSH key/agent auth
    DO_SSH_KNOWN_HOSTS Known-hosts file, defaults to ~/.ssh/known_hosts
    DO_REMOTE_DIR     Remote project directory, defaults to /var/www/buykori-adsync
"""

from __future__ import annotations

import argparse
import os
import posixpath
import stat
import subprocess
from pathlib import Path

import paramiko


DEFAULT_REMOTE_DIR = "/var/www/buykori-adsync"
EXCLUDED_PREFIXES = (
    ".git/",
    "client-portal/",
    "admin-portal/",
    "scratch/",
)
EXCLUDED_FILES = {
    ".env",
    "buykori-adsync-updated.zip",
}
DEPLOYABLE_PREFIXES = (
    "app/",
    "migrations/",
    "wordpress-plugin/",
)
DEPLOYABLE_FILES = {
    "alembic.ini",
    "requirements.txt",
}


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def changed_files(base: str, *, include_working_tree: bool = False) -> list[tuple[str, str]]:
    diff_target = base if include_working_tree else f"{base}..HEAD"
    output = run_git(["diff", "--name-status", diff_target])
    changes: list[tuple[str, str]] = []

    for line in output.splitlines() if output else []:
        parts = line.split("\t")
        status_code = parts[0]
        status = status_code[0]
        path = parts[-1]
        if should_skip(path):
            continue
        changes.append((status, path))

    if include_working_tree:
        untracked = run_git(["ls-files", "--others", "--exclude-standard"])
        known_paths = {path for _, path in changes}
        for path in untracked.splitlines() if untracked else []:
            if path in known_paths or should_skip(path):
                continue
            changes.append(("A", path))

    return changes


def local_deployable_changes() -> list[str]:
    """Return staged, unstaged, and untracked production paths omitted without --working-tree."""
    paths = set()
    commands = (
        ["diff", "--name-only"],
        ["diff", "--cached", "--name-only"],
        ["ls-files", "--others", "--exclude-standard"],
    )
    for command in commands:
        output = run_git(command)
        for path in output.splitlines() if output else []:
            if not should_skip(path):
                paths.add(path)
    return sorted(paths)


def should_skip(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return (
        not (
            normalized in DEPLOYABLE_FILES
            or any(normalized.startswith(prefix) for prefix in DEPLOYABLE_PREFIXES)
        )
        or
        normalized in EXCLUDED_FILES
        or normalized.endswith(".pyc")
        or any(normalized.startswith(prefix) for prefix in EXCLUDED_PREFIXES)
    )


def ensure_remote_dir(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
    current = ""
    for part in remote_dir.strip("/").split("/"):
        current += f"/{part}"
        try:
            sftp.mkdir(current)
        except OSError:
            pass


def remove_remote_path(sftp: paramiko.SFTPClient, remote_path: str) -> None:
    try:
        info = sftp.stat(remote_path)
    except FileNotFoundError:
        return

    if stat.S_ISDIR(info.st_mode):
        for entry in sftp.listdir_attr(remote_path):
            remove_remote_path(sftp, posixpath.join(remote_path, entry.filename))
        sftp.rmdir(remote_path)
    else:
        sftp.remove(remote_path)


def upload_file(sftp: paramiko.SFTPClient, local_root: Path, remote_root: str, rel_path: str) -> None:
    local_path = local_root / rel_path
    if not local_path.is_file():
        return
    remote_path = posixpath.join(remote_root, rel_path.replace("\\", "/"))
    ensure_remote_dir(sftp, posixpath.dirname(remote_path))
    sftp.put(str(local_path), remote_path)
    print(f"uploaded {rel_path}")


def run_remote(ssh: paramiko.SSHClient, command: str) -> int:
    stdin, stdout, stderr = ssh.exec_command(command)
    for line in stdout:
        print(line, end="")
    err = stderr.read().decode("utf-8", errors="replace").strip()
    if err:
        print(err)
    return stdout.channel.recv_exit_status()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="HEAD~1", help="Git ref to diff against")
    parser.add_argument("--working-tree", action="store_true", help="Include staged, unstaged, and untracked production files")
    parser.add_argument("--dry-run", action="store_true", help="Print planned upload/delete/restart steps without connecting")
    parser.add_argument("--skip-migrations", action="store_true")
    parser.add_argument("--skip-restart", action="store_true")
    args = parser.parse_args()

    local_root = Path(run_git(["rev-parse", "--show-toplevel"]))
    remote_root = os.environ.get("DO_REMOTE_DIR", DEFAULT_REMOTE_DIR)
    host = os.environ.get("DO_SSH_HOST")
    username = os.environ.get("DO_SSH_USER")
    password = os.environ.get("DO_SSH_PASSWORD")

    changes = changed_files(args.base, include_working_tree=args.working_tree)
    if not args.working_tree:
        local_changes = local_deployable_changes()
        if local_changes:
            print(
                f"WARNING: {len(local_changes)} local deployable file change(s) are omitted. "
                "Re-run with --working-tree to include them."
            )
    if not changes:
        print("No deployable tracked file changes found.")
        return 0

    if not host or not username:
        print("Set DO_SSH_HOST and DO_SSH_USER before running a live deploy.")
        return 2
    if username == "root" and os.environ.get("ALLOW_ROOT_DEPLOY", "").lower() not in ("true", "1", "yes"):
        print("Refusing root deploy by default. Use a limited deploy user or set ALLOW_ROOT_DEPLOY=true for a controlled migration window.")
        return 2
    if password and os.environ.get("ALLOW_SSH_PASSWORD_DEPLOY", "").lower() not in ("true", "1", "yes"):
        print("Refusing password-based SSH deploy by default. Use SSH keys or set ALLOW_SSH_PASSWORD_DEPLOY=true temporarily.")
        return 2

    if args.dry_run:
        print(f"Dry run against base {args.base}")
        for status_code, rel_path in changes:
            action = "delete" if status_code == "D" else "upload"
            print(f"{action}: {rel_path}")
        if any(rel_path == "requirements.txt" for _, rel_path in changes):
            print("remote: install Python dependencies")
        if not args.skip_migrations:
            print("remote: run alembic upgrade head")
        if not args.skip_restart:
            print("remote: restart buykori-web and buykori-worker:*")
        return 0

    ssh = paramiko.SSHClient()
    known_hosts_path = Path(os.environ.get("DO_SSH_KNOWN_HOSTS", str(Path.home() / ".ssh" / "known_hosts")))
    if not known_hosts_path.exists():
        print(f"Known-hosts file not found: {known_hosts_path}")
        return 2
    ssh.load_host_keys(str(known_hosts_path))
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    ssh.connect(
        host,
        username=username,
        password=password,
        timeout=20,
        look_for_keys=True,
        allow_agent=True,
    )
    sftp = ssh.open_sftp()

    try:
        for status_code, rel_path in changes:
            remote_path = posixpath.join(remote_root, rel_path.replace("\\", "/"))
            if status_code == "D":
                remove_remote_path(sftp, remote_path)
                print(f"deleted {rel_path}")
            else:
                upload_file(sftp, local_root, remote_root, rel_path)
    finally:
        sftp.close()

    commands = [f"cd {remote_root}"]
    if any(rel_path == "requirements.txt" for _, rel_path in changes):
        commands.append("./venv/bin/pip install -r requirements.txt")
    if not args.skip_migrations:
        commands.append("./venv/bin/alembic upgrade head")
    if not args.skip_restart:
        commands.append("sudo supervisorctl restart buykori-web buykori-worker:*")
        commands.append("sudo supervisorctl status")

    if len(commands) > 1:
        exit_code = run_remote(ssh, " && ".join(commands))
    else:
        exit_code = 0
    ssh.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
