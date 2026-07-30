# Security Policy

ARIADNE is not yet published as a stable public release.

For the Japanese version, see [SECURITY.md](SECURITY.md).

## Supported Versions

| Version | Supported |
| --- | --- |
| `0.1.x` pre-release/runtime foundation | Best-effort security review |

## Reporting a Vulnerability

Security and vulnerability reports are accepted through GitHub Security Advisories.

Do not post vulnerability details, exploit steps, secrets, credentials, or private repository information in public issues, GitHub Discussions, pull requests, or public comments.

When reporting, include:

- Affected commit, branch, or release candidate.
- Reproduction steps.
- Expected and observed behavior.
- Impact assessment.
- Whether secrets, credentials, customer data, or private repository information may be involved.

## General Contact

Use GitHub Discussions for bug reports, questions, proposals, and usage discussions.
If the topic includes security-sensitive details, use GitHub Security Advisories instead of Discussions.

## Public Disclosure

Security issues should not be marked release-ready until a human reviewer confirms:

- The affected files and artifacts are identified.
- No secrets or private data were committed.
- A mitigation or documented limitation exists.
- Release notes do not disclose exploit details prematurely.

## Release Audit

Before publication, run the local release validator:

```powershell
aiwfctl release validate
```
