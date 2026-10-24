
#!/usr/bin/env python3
"""
Generate a proposed portfolio improvement using the OpenAI API.

This script analyzes local repository files and asks OpenAI to propose
a focused code improvement. It does not execute generated code, commit,
or push changes.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from openai import OpenAI


MAX_FILE_SIZE = 40_000
MAX_TOTAL_CHARS = 120_000

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".next",
    "coverage",
}

ALLOWED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".md",
    ".html",
    ".css",
    ".yml",
    ".yaml",
    ".sql",
}


def collect_files(repo_path: Path) -> list[Path]:
    """Collect a bounded set of relevant text files."""
    files: list[Path] = []

    for path in sorted(repo_path.rglob("*")):
        if not path.is_file():
            continue

        if any(part in IGNORED_DIRS for part in path.parts):
            continue

        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        if path.stat().st_size > MAX_FILE_SIZE:
            continue

        files.append(path)

    return files


def read_repository(repo_path: Path) -> str:
    """Read relevant repository files within a context-size limit."""
    sections: list[str] = []
    total_chars = 0

    for path in collect_files(repo_path):
        relative_path = path.relative_to(repo_path)

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        section = f"\n--- FILE: {relative_path} ---\n{content}\n"

        if total_chars + len(section) > MAX_TOTAL_CHARS:
            break

        sections.append(section)
        total_chars += len(section)

    return "\n".join(sections)


def get_git_status(repo_path: Path) -> str:
    """Return the repository's current git status."""
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip() or "Working tree is clean."


def generate_improvement(
    repo_path: Path,
    task: str,
    model: str,
) -> str:
    """Ask OpenAI for a focused improvement proposal."""
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is missing.")

    client = OpenAI(api_key=api_key)

    repository_context = read_repository(repo_path)
    git_status = get_git_status(repo_path)

    if not repository_context.strip():
        raise RuntimeError("No supported repository files were found.")

    instructions = """
You are a careful senior software engineer improving a portfolio project.

Inspect the supplied repository context and identify one meaningful,
evidence-based improvement.

Rules:
- Do not invent bugs or claim to have run tests.
- Prefer a small, coherent change.
- Respect the repository's existing stack and conventions.
- Consider security, privacy, input validation, error handling, and tests.
- Do not expose secrets or reproduce private credentials.
- Do not rewrite unrelated code.
- If no meaningful improvement is supported by the context, say so.
- Do not execute commands or claim that files have been modified.

Return:
1. The problem or opportunity and evidence.
2. The proposed solution.
3. The exact unified diff, if a change is justified.
4. Tests that should be run.
5. Risks and limitations.

The diff must use standard unified diff format and include file paths.
"""

    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=(
            f"Repository path: {repo_path}\n\n"
            f"Current git status:\n{git_status}\n\n"
            f"Task:\n{task}\n\n"
            f"Repository files:\n{repository_context}"
        ),
    )

    return response.output_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a proposed repository improvement with OpenAI."
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="Path to the target Git repository.",
    )

    parser.add_argument(
        "--task",
        required=True,
        help="Description of the improvement to investigate.",
    )

    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_MODEL", "gpt-4.1"),
        help="OpenAI model name.",
    )

    parser.add_argument(
        "--output",
        default="proposed-improvement.md",
        help="File where the proposal will be saved.",
    )

    args = parser.parse_args()

    repo_path = Path(args.repo).resolve()

    if not repo_path.is_dir():
        raise SystemExit(f"Repository directory does not exist: {repo_path}")

    result = generate_improvement(
        repo_path=repo_path,
        task=args.task,
        model=args.model,
    )

    output_path = Path(args.output).resolve()
    output_path.write_text(result, encoding="utf-8")

    print(f"Proposal saved to: {output_path}")


if __name__ == "__main__":
    main()

