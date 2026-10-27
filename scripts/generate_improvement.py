
import argparse
import os
import sys
from pathlib import Path

from google import genai


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-path", default=".")
    parser.add_argument("--output", default="improvement-proposal.md")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("ERROR: GEMINI_API_KEY environment variable is missing.")

    repo_path = Path(args.repo_path).resolve()
    output_path = Path(args.output).resolve()

    excluded_dirs = {
        ".git", ".github", "node_modules", "venv",
        ".venv", "__pycache__", "dist", "build"
    }
    allowed_suffixes = {
        ".py", ".js", ".jsx", ".ts", ".tsx",
        ".json", ".md", ".html", ".css", ".yml", ".yaml"
    }

    snippets = []
    total_chars = 0
    max_chars = 40000

    for path in sorted(repo_path.rglob("*")):
        if not path.is_file():
            continue
        if any(part in excluded_dirs for part in path.parts):
            continue
        if path.suffix.lower() not in allowed_suffixes:
            continue
        if path.resolve() == output_path:
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        relative_path = path.relative_to(repo_path)
        block = f"\n--- FILE: {relative_path} ---\n{content}\n"
        if total_chars + len(block) > max_chars:
            break

        snippets.append(block)
        total_chars += len(block)

    if not snippets:
        sys.exit("ERROR: No eligible source files found to review.")

    prompt = f"""
You are a careful senior software engineer reviewing a GitHub project.

Review the supplied source files and identify ONE meaningful, low-risk
improvement that genuinely improves correctness, usability, maintainability,
security, or test coverage.

Do not invent missing files or claim tests were run when they were not.
If no worthwhile improvement is supported by the available context, say
NO_CHANGE_NEEDED and explain why.

Return:
1. A short explanation of the improvement and its benefit.
2. A unified diff in a fenced diff block, using correct repository-relative
   file paths.
3. Any tests that should be run to validate the change.

Do not include secrets or request credentials.

Repository source context:
{''.join(snippets)}
"""

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )

    result = response.text or ""
    if not result.strip():
        sys.exit("ERROR: Gemini returned an empty response.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")
    print(f"Proposal saved to: {output_path}")
    print(result)


if __name__ == "__main__":
    main()
