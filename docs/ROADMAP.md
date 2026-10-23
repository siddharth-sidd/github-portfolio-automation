# Roadmap: from scheduled prompts to AI-generated pull requests

## Stage 1 — Safe planning scaffold (this version)

- Scheduled daily tasks rotate through an explicit allowlist.
- Biweekly runs open an approval-required new-project proposal.
- Workflows only read controller files and write issues in this repository.
- Python tests validate deterministic selection and review-only safety policy.

## Stage 2 — AI-assisted implementation (not enabled)

Before enabling this stage, the repository owner must select an AI provider, explicitly create an Actions secret for its API key, and approve using that provider for the portfolio. Then implement:

1. A pinned provider SDK and a documented model choice.
2. Request timeouts, bounded retries, output size limits, and a per-run spend limit.
3. Structured output requiring target repository, rationale, file plan, tests, and rollback notes.
4. A separate unprivileged worker job for reading target code and generating a patch.
5. A validator that rejects path traversal, secret-like values, oversized diffs, binaries, and workflow/permission modifications unless explicitly allowed.
6. Test execution in an unprivileged sandbox with no write token and no secrets from target repos.
7. Upload an artifact for review; then a separately scoped publisher job opens a PR only after validation.
8. PR body must include test results, skipped checks, risks, and an explicit note where human verification remains necessary.

Never give an AI worker a token capable of writing to every repository. Use a narrowly scoped GitHub App or per-repository token and a strict repository allowlist.

## Stage 3 — Multi-repository pull-request publishing (not enabled)

- Add only approved repositories to the allowlist after confirming access.
- Use least-privilege credentials sufficient to create branches and pull requests, not to merge.
- Never push to default branches, auto-merge, release, deploy, or create new repositories.
- Add duplicate-task detection and an open-PR check before any run.
- Require successful project-specific CI before requesting human review.

## Stage 4 — Observability and upkeep

- Track last selected repo and outcomes to avoid repetitive or empty issues.
- Add a weekly report of opened tasks/PRs, validation failures, and meaningful changes.
- Review dependency pins, Actions versions, security posture, and logs periodically.

## Important limitation

The current controller only creates task/proposal issues. It does not autonomously inspect target repositories, write code, or create PRs. A schedule alone is not an AI coding agent; provider integration and a safely isolated PR publisher remain to be implemented and approved.
