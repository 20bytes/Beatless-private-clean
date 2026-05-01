"""Local readiness check for Beatless modules.

Run this before enabling cron or GitHub automation:

    python3 hermes-scripts/preflight.py
    python3 hermes-scripts/preflight.py --create-dirs
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

from beatless_config import CONFIG


def _ok(value: bool) -> str:
    return "PASS" if value else "WARN"


def _fail(value: bool) -> str:
    return "PASS" if value else "FAIL"


def _cmd(name: str) -> bool:
    return shutil.which(name) is not None


def _run_quiet(args: list[str], timeout: int = 10, env: dict[str, str] | None = None) -> bool:
    try:
        result = subprocess.run(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            env=env,
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _check_path(path: Path, create: bool = False) -> bool:
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path.exists()


def _line(section: str, name: str, status: str, detail: str = "") -> None:
    print(f"{section:<10} {name:<28} {status:<5} {detail}")


def _env_present(name: str) -> bool:
    return os.environ.get(name) not in (None, "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--create-dirs",
        action="store_true",
        help="create non-destructive local runtime directories",
    )
    args = ap.parse_args()

    print("Beatless local preflight")
    print(f"repo:      {CONFIG.repo_root}")
    print(f"workspace: {CONFIG.workspace}")
    print(f"shared:    {CONFIG.shared_dir}")
    print()

    fail_count = 0

    core_checks = [
        ("python3", _cmd("python3"), "required for wake-gate scripts"),
        ("git", _cmd("git"), "required for repo workflows"),
        ("codex", _cmd(CONFIG.codex_bin), f"primary executor: {CONFIG.codex_bin}"),
        ("uv", _cmd("uv"), "required by experiment commands"),
        ("node", _cmd("node"), "required by Hermes/shared JS helpers"),
        ("claude", _cmd(CONFIG.claude_bin), "optional legacy fallback"),
        ("nvidia-smi", _cmd("nvidia-smi"), "required only for GPU experiment automation"),
    ]
    blocking = {"python3", "git", "codex"}
    if CONFIG.primary_executor != "codex":
        blocking.add("claude")
    for name, passed, detail in core_checks:
        _line("core", name, _fail(passed) if name in blocking else _ok(passed), detail)
        if name in blocking and not passed:
            fail_count += 1

    _line(
        "core",
        "primary executor",
        _fail(CONFIG.primary_executor == "codex"),
        CONFIG.primary_executor,
    )
    if CONFIG.primary_executor != "codex":
        fail_count += 1
    _line(
        "core",
        "codex model",
        "INFO",
        f"{CONFIG.codex_model}, reasoning={CONFIG.codex_reasoning_effort}, sandbox={CONFIG.codex_sandbox}",
    )
    _line("core", "codex home", "INFO", str(CONFIG.codex_home))
    codex_env = os.environ.copy()
    codex_env["CODEX_HOME"] = str(CONFIG.codex_home)
    try:
        CONFIG.codex_home.mkdir(parents=True, exist_ok=True)
    except OSError:
        codex_ready = False
    else:
        codex_ready = _run_quiet(
            [
                CONFIG.codex_bin,
                "-m",
                CONFIG.codex_model,
                "-c",
                f'model_reasoning_effort="{CONFIG.codex_reasoning_effort}"',
                "--ask-for-approval",
                "never",
                "--sandbox",
                "read-only",
                "exec",
                "--ephemeral",
                "-C",
                str(CONFIG.repo_root),
                "Reply exactly CODEX_READY",
            ],
            timeout=30,
            env=codex_env,
        )
    _line("core", "codex ready", _fail(codex_ready), "non-destructive readiness check")
    if not codex_ready:
        fail_count += 1
    _line(
        "core",
        "claude fallback",
        "INFO",
        "enabled" if CONFIG.allow_claude_fallback else "disabled",
    )

    print()
    gh_installed = _cmd("gh")
    _line("github", "gh cli", _fail(gh_installed), "required for GitHub PR/follow-up")
    if not gh_installed:
        fail_count += 1
    else:
        _line("github", "gh auth", _ok(_run_quiet(["gh", "auth", "status"])), "must pass before real PR automation")
    _line(
        "github",
        "author",
        _ok(bool(CONFIG.github_author)),
        f"{CONFIG.github_author or 'not set'} (set BEATLESS_GITHUB_AUTHOR)",
    )

    print()
    runtime_dirs = [
        ("hermes shared", CONFIG.shared_dir),
        ("workspace", CONFIG.workspace),
        ("contrib root", CONFIG.contrib_root),
        ("pr stage root", CONFIG.pr_stage_root),
        ("research dir", CONFIG.research_dir),
        ("obsidian vault", CONFIG.obsidian_vault),
        ("literature dir", CONFIG.literature_dir),
    ]
    for name, path in runtime_dirs:
        exists = _check_path(path, args.create_dirs)
        _line("paths", name, _ok(exists), str(path))
    _line("paths", "blog dir", _ok(CONFIG.blog_dir.exists()), str(CONFIG.blog_dir))
    _line("paths", "blog posts", _ok(CONFIG.blog_posts_dir.exists()), str(CONFIG.blog_posts_dir))

    print()
    paper_env_ok = bool(CONFIG.zotero_api_key and CONFIG.zotero_user_id)
    _line("papers", "zotero api", _ok(paper_env_ok), "ZOTERO_API_KEY + ZOTERO_USER_ID")
    _line("papers", "zotero web user", _ok(bool(CONFIG.zotero_web_username)), "optional: ZOTERO_WEB_USERNAME")
    _line("papers", "default collection", _ok(bool(CONFIG.zotero_default_collection)), CONFIG.zotero_default_collection)

    print()
    _line("blog", "pnpm", _ok(_cmd("pnpm")), "required only if building/publishing blog")
    _line("hermes", "hermes cli", _ok(_cmd("hermes")), "required only for scheduled gateway mode")

    print()
    if args.create_dirs:
        print("Created missing non-destructive runtime directories where needed.")
    if fail_count:
        print(f"Blocking failures: {fail_count}")
        return 1
    print("Blocking failures: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
