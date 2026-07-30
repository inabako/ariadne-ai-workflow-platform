# Contributing

Thank you for considering a contribution to ARIADNE.

ARIADNE is developed as an evidence-oriented AI workflow platform. Contributions should preserve the repository's core responsibilities: intent capture, context-first execution, reviewable artifacts, Human Gates, recovery, and reproducible evidence.

For the Japanese version, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Before You Start

- Read [docs/README.md](docs/README.md) for the documentation map.
- Read [docs/architecture/overview.md](docs/architecture/overview.md) for the platform structure.
- Check [docs/release/release-policy.md](docs/release/release-policy.md) before release-facing changes.
- Keep generated local work under ignored workspaces such as `work/`, `logs/`, or `db/rag/` unless a document explicitly says the artifact is tracked.

## Contribution Flow

1. Open or reference an issue that explains the intent, expected impact, and affected area.
2. Keep changes reviewable. Separate runtime behavior, tests, documentation, and release metadata when the scopes are independent.
3. Add or update tests for behavior changes.
4. Update docs when implementation behavior, commands, schemas, or artifact locations change.
5. Run the relevant checks before requesting review.

## Pull Request Expectations

- Describe the intent, scope, decision, and impact.
- Link related issues, design notes, or evidence.
- Include test commands and results.
- Call out Human Gate decisions, security-sensitive behavior, and release-impacting changes.

## Licensing of Contributions

By contributing, you agree that your contribution may be distributed under `AGPL-3.0-or-later`, the repository license in effect for ARIADNE.

Do not change license identifiers, package license metadata, or the root `LICENSE` as part of a normal contribution unless the project owner has approved that license decision.

Generated outputs created by using ARIADNE as a tool are not automatically assigned the ARIADNE repository license solely because ARIADNE was used. See [docs/legal/generated-artifacts.md](docs/legal/generated-artifacts.md).

## Code and Documentation Standards

- Prefer existing runtime and workflow patterns over new abstractions.
- Preserve UTF-8 text encoding.
- Do not add secrets, customer information, private URLs, local absolute paths, or non-public project details to tracked files.
- Keep user-facing reports and review artifacts in Japanese unless a document requires English.
- Do not describe unimplemented features as complete.

## Release Checks

For release-facing changes, run:

```powershell
aiwfctl release validate
```
