"""Helpers for shaping the WordPress plugin package served to customers."""

from __future__ import annotations

import os


PROTECTED_PACKAGE_SUFFIXES = {".php", ".js", ".css"}


def plugin_protection_enabled() -> bool:
    return os.getenv("PLUGIN_PROTECTED_PACKAGE", "true").lower() in {"1", "true", "yes"}


def protect_plugin_package_content(archive_name: str, content: bytes, *, enabled: bool | None = None) -> bytes:
    if enabled is None:
        enabled = plugin_protection_enabled()
    if not enabled:
        return content

    lower_name = archive_name.lower()
    if not any(lower_name.endswith(suffix) for suffix in PROTECTED_PACKAGE_SUFFIXES):
        return content

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return content

    preserve_header = lower_name.endswith("/buykori-adsync.php")
    return _strip_comment_only_lines(text, preserve_plugin_header=preserve_header).encode("utf-8")


def _strip_comment_only_lines(text: str, *, preserve_plugin_header: bool = False) -> str:
    lines = text.splitlines()
    output: list[str] = []
    in_block_comment = False
    preserving_header = preserve_plugin_header
    saw_plugin_header = False
    blank_pending = False

    for line in lines:
        stripped = line.strip()

        if preserving_header:
            output.append(line)
            if "Plugin Name:" in line:
                saw_plugin_header = True
            if saw_plugin_header and "*/" in line:
                preserving_header = False
            continue

        if in_block_comment:
            if "*/" in stripped:
                in_block_comment = False
            continue

        if not stripped:
            if not blank_pending:
                output.append("")
                blank_pending = True
            continue

        starts_block = stripped.startswith("/*")
        ends_block = "*/" in stripped
        if starts_block:
            if not ends_block:
                in_block_comment = True
            continue

        if stripped.startswith(("//", "#", "*", "*/")):
            continue

        output.append(line)
        blank_pending = False

    return "\n".join(output).rstrip() + "\n"
