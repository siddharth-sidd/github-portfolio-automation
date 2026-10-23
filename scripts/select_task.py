#!/usr/bin/env python3
"""Create deterministic, review-first portfolio task descriptions.

This script does not contact GitHub, call an AI provider, or change target repos.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "repositories.json"


def load_config() -> dict:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    repos = data.get("repositories")
    if not isinstance(repos, list) or not repos:
        raise ValueError("config must contain a non-empty repositories list")
    for item in repos:
        if not isinstance(item.get("full_name"), str) or "/" not in item["full_name"]:
            raise ValueError("every repository needs a full_name in owner/name form")
    return data


def choose_repository(config: dict, when: date) -> dict:
    """Rotate one repository per calendar day, stable across reruns."""
    repos = config["repositories"]
    index = when.toordinal() % len(repos)
    return repos[index]


def daily_task(config: dict, when: date) -> str:
    repo = choose_repository(config, when)
    focus = ", ".join(repo.get("focus_areas", [])) or "bugs, tests, maintainability"
    stacks = ", ".join(repo.get("stacks", [])) or "the project's existing stack"
    return f"""## Daily portfolio improvement proposal

**Target repository:** `{repo['full_name']}`  
**Date:** {when.isoformat()}  
**Mode:** review-only; create a pull request only after implementation and checks

### Task for the coding agent or maintainer

Inspect the target repository's current code, README, open issues, and tests before choosing one narrowly scoped improvement. Use the existing stack ({stacks}). Candidate focus areas: {focus}.

Select a concrete user-facing bug, reliability concern, accessibility issue, useful missing test, or maintainability improvement supported by evidence in the repository. Do not invent a defect or rewrite working code for activity alone. If no meaningful change is justified, comment that no-op is preferred and close this task without a code change.

### Acceptance criteria

- Explain the current behavior and why the proposed change matters.
- Keep scope to one coherent improvement and normally no more than 8 files.
- Add or update automated tests for behavior changes.
- Run the project's relevant test, lint, and build commands where safe and feasible; report exact commands and outcomes.
- Update documentation when behavior or setup changes.
- Open a pull request with summary, rationale, test evidence, and known limitations. Never push directly to the default branch or merge automatically.
- Do not expose credentials, copy private data, or execute untrusted scripts with privileged tokens.
"""


def biweekly_task(when: date) -> str:
    return f"""## Biweekly new-project proposal

**Proposal date:** {when.isoformat()}  
**Approval required:** yes — do not create a repository automatically

Propose one original, portfolio-quality project that complements the current portfolio and demonstrates a different useful skill or stack where appropriate (for example, Python/Django, SQL, React/TypeScript, or MERN). First check the portfolio to avoid duplicating existing work.

### Required proposal

- Problem statement and intended users.
- Unique scope and why it complements the existing portfolio.
- Stack and architecture, including why each major technology is appropriate.
- MVP features and explicit non-goals.
- Data model/API design and security/privacy considerations.
- Test strategy, CI checks, accessibility considerations where applicable.
- A realistic phased implementation plan and demo/deployment plan.
- Acceptance criteria and risks.

Do not create a repository, add secrets, grant permissions, deploy, or spend on services without explicit approval. Wait for the owner to approve the proposal before implementation.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=date.today().isoformat(), help="date in YYYY-MM-DD form")
    parser.add_argument("--biweekly", action="store_true", help="generate a new-project proposal instead")
    args = parser.parse_args()
    when = date.fromisoformat(args.date)
    config = load_config()
    print(biweekly_task(when) if args.biweekly else daily_task(config, when))


if __name__ == "__main__":
    main()
