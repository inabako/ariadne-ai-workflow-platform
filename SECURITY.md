# Security Policy

ARIADNEは、まだstable public releaseとして公開されていません。

英語版は [SECURITY.en.md](SECURITY.en.md) を参照してください。

## Supported Versions

| Version | Supported |
| --- | --- |
| `0.1.x` pre-release/runtime foundation | best-effort security review |

## Vulnerability Reporting

セキュリティ・脆弱性の連絡は、GitHub Security Advisoriesで受け付けます。

脆弱性の詳細、exploit手順、secret、credential、private repository informationは、public issue、GitHub Discussions、pull request、公開コメントには投稿しないでください。

報告には、可能な範囲で次を含めてください。

- 影響するcommit、branch、release candidate。
- 再現手順。
- 期待する動作と観測された動作。
- impact assessment。
- secret、credential、customer data、private repository informationが関係する可能性。

## General Contact

バグ報告、質問、提案、使い方の相談はGitHub Discussionsで受け付けます。
security-sensitiveな内容が含まれる場合は、DiscussionsではなくGitHub Security Advisoriesを使用してください。

## Public Disclosure

security issueは、人間reviewerが次を確認するまでrelease-readyにしないでください。

- 影響するfilesとartifactsが特定されている。
- secretまたはprivate dataがcommitされていない。
- mitigationまたはdocumented limitationがある。
- release notesがexploit detailsを早期に公開していない。

## Release Audit

公開前にはlocal release validatorを実行してください。

```powershell
aiwfctl release validate
```
