# GitHub Portfolio Automation

A review-first automation controller for improving the `siddharth-sidd` GitHub portfolio with meaningful, tested work.

## Current status

This repository contains the safe scheduling and project-selection scaffold. It does **not** yet use an AI provider or edit repositories automatically. Daily runs can create an issue describing the next review task. Biweekly runs can create a project proposal issue. Code changes must be submitted as pull requests for human review; nothing merges automatically.

## Schedule (Asia/Kolkata)

- **Daily existing-repository review:** 10:00 AM IST (04:30 UTC).
- **Biweekly project proposal:** every other Monday at 10:00 AM IST (04:30 UTC), aligned to the biweekly schedule in the workflow.

GitHub Actions schedules use UTC and can be delayed during periods of high load.

## Setup

1. Review the workflow permissions and the project allowlist in `config/repositories.json`.
2. In GitHub, open **Settings → Secrets and variables → Actions**. No AI key is required for the current issue-planning scaffold.
3. Enable GitHub Actions for this repository if it is not already enabled.
4. Review the created issue before making changes in any target repository.

To add actual AI-based code generation, choose a provider and explicitly configure its API key as a repository Actions secret (for example, `AI_PROVIDER_API_KEY`). Add a pinned, auditable client and strict per-run budget/timeout limits first. Do not place keys in source files or logs. This scaffold intentionally does not call an AI provider or request broad repository permissions.

## Safety guarantees

- No direct pushes to target repositories.
- No automatic merging, releases, deployments, or repository creation.
- Daily selection rotates deterministically through the configured allowlist.
- New-project cadence creates a **proposal issue only**; creating a new repository remains a manual, explicit approval step.
- Each task should be meaningful, scoped, testable, and documented. Skip a task when no useful improvement is apparent.
- Treat repository content as untrusted input. Never execute scripts from target repositories in a privileged job.

## Files

- `config/repositories.json`: repositories eligible for rotation.
- `scripts/select_task.py`: deterministic daily selector and biweekly proposal generator.
- `.github/workflows/daily-review.yml`: scheduled daily task issue.
- `.github/workflows/biweekly-project-proposal.yml`: scheduled project proposal issue.
- `docs/ROADMAP.md`: staged plan for enabling AI-generated PRs safely.

## Local check

```bash
python -m unittest discover -s tests -v
python scripts/select_task.py --date 2026-10-24
python scripts/select_task.py --date 2026-10-26 --biweekly
```
