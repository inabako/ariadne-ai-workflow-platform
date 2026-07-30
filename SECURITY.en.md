# Security Policy

ARIADNE is not yet published as a stable public release.

For the Japanese version, see [SECURITY.md](SECURITY.md).

## Supported Versions

| Version | Supported |
| --- | --- |
| `0.1.x` pre-release/runtime foundation | Best-effort security review |

## Reporting a Vulnerability

The public security contact is not yet finalized. Until a public contact is defined, do not publish vulnerability details in public issues.

Use a private project-owner channel for reports, and include:

- Affected commit, branch, or release candidate.
- Reproduction steps.
- Expected and observed behavior.
- Impact assessment.
- Whether secrets, credentials, customer data, or private repository information may be involved.

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
