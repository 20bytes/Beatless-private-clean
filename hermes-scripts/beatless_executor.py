"""Primary executor bridge for Beatless wake-gate scripts.

The active architecture routes heavy work to the local Codex CLI. Claude fields
remain only for explicit legacy fallback. Business scripts should call
`run_primary()` instead of assembling raw executor commands themselves.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import subprocess

from beatless_config import CONFIG


@dataclass(frozen=True)
class ExecutorResult:
    executor: str
    args: list[str]
    returncode: int
    stdout: str
    stderr: str


def _codex_model_args() -> list[str]:
    return [
        "-m",
        CONFIG.codex_model,
        "-c",
        f'model_reasoning_effort="{CONFIG.codex_reasoning_effort}"',
    ]


def run_codex(
    prompt: str,
    *,
    cwd: str | Path,
    timeout: int | None = None,
    sandbox: str | None = None,
) -> ExecutorResult:
    """Run Codex non-interactively with stdin prompt payload."""
    cwd_path = Path(cwd).expanduser()
    try:
        CONFIG.codex_home.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return ExecutorResult(
            executor="codex",
            args=[],
            returncode=2,
            stdout="",
            stderr=f"Failed to prepare CODEX_HOME at {CONFIG.codex_home}: {exc}",
        )
    sandbox_mode = sandbox or CONFIG.codex_sandbox
    timeout = timeout or CONFIG.codex_timeout_seconds
    env = os.environ.copy()
    env["CODEX_HOME"] = str(CONFIG.codex_home)
    args = [
        CONFIG.codex_bin,
        *_codex_model_args(),
        "--ask-for-approval",
        "never",
        "--sandbox",
        sandbox_mode,
        "exec",
        "--skip-git-repo-check",
        "--ephemeral",
        "-C",
        str(cwd_path),
        "-",
    ]
    try:
        result = subprocess.run(
            args,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd_path),
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        return ExecutorResult(
            executor="codex",
            args=args,
            returncode=124,
            stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
            stderr=((exc.stderr or "") if isinstance(exc.stderr, str) else "")
            + f"\nCodex timed out after {timeout}s",
        )

    return ExecutorResult(
        executor="codex",
        args=args,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def run_claude_fallback(
    prompt: str,
    *,
    cwd: str | Path,
    timeout: int | None = None,
) -> ExecutorResult:
    """Run the legacy Claude fallback path when explicitly enabled."""
    cwd_path = Path(cwd).expanduser()
    timeout = timeout or CONFIG.codex_timeout_seconds
    env = os.environ.copy()
    args = [
        CONFIG.claude_bin,
        "-p",
        "--model",
        CONFIG.claude_model,
        "--dangerously-skip-permissions",
        prompt,
    ]
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd_path),
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        return ExecutorResult(
            executor="claude",
            args=args,
            returncode=124,
            stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else "",
            stderr=((exc.stderr or "") if isinstance(exc.stderr, str) else "")
            + f"\nClaude fallback timed out after {timeout}s",
        )

    return ExecutorResult(
        executor="claude",
        args=args,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def run_primary(
    prompt: str,
    *,
    cwd: str | Path,
    mode: str = "workspace-write",
    timeout: int | None = None,
) -> ExecutorResult:
    """Run the configured primary executor with optional Claude fallback."""
    timeout = timeout or CONFIG.codex_timeout_seconds

    if CONFIG.primary_executor == "codex":
        result = run_codex(prompt, cwd=cwd, timeout=timeout, sandbox=mode)
        if result.returncode == 0 or not CONFIG.allow_claude_fallback:
            return result
        return run_claude_fallback(prompt, cwd=cwd, timeout=timeout)

    if CONFIG.primary_executor == "claude":
        return run_claude_fallback(prompt, cwd=cwd, timeout=timeout)

    return ExecutorResult(
        executor=CONFIG.primary_executor,
        args=[],
        returncode=2,
        stdout="",
        stderr=f"Unsupported BEATLESS_PRIMARY_EXECUTOR={CONFIG.primary_executor!r}",
    )


def run_codex_exec(
    prompt: str,
    *,
    cwd: str | Path,
    timeout: int,
    sandbox: str | None = None,
) -> ExecutorResult:
    """Backward-compatible alias for older imports."""
    return run_codex(prompt, cwd=cwd, timeout=timeout, sandbox=sandbox)


def executor_label() -> str:
    return (
        f"Codex CLI ({CONFIG.codex_model}, "
        f"reasoning={CONFIG.codex_reasoning_effort}, sandbox={CONFIG.codex_sandbox})"
    )


def load_repo_text(relative_path: str, *, max_chars: int = 60_000) -> str:
    """Read a repository-local instruction file for embedding in a prompt."""
    path = CONFIG.repo_root / relative_path
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return f"[missing instruction file: {relative_path}]"
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n\n[truncated: {relative_path} exceeded {max_chars} chars]\n"
