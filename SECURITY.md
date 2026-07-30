# Security Policy

ARIADNEは、まだstable public releaseとして公開されていません。

英語版は [SECURITY.en.md](SECURITY.en.md) を参照してください。

## Supported Versions

| Version | Supported |
| --- | --- |
| `0.1.x` pre-release/runtime foundation | best-effort security review |

## Vulnerability Reporting

公開security contactはまだ確定していません。公開contactが定義されるまでは、脆弱性の詳細をpublic issueに投稿しないでください。

報告はprivate project-owner channelを使用し、可能な範囲で次を含めてください。

- 影響するcommit、branch、release candidate。
- 再現手順。
- 期待する動作と観測された動作。
- impact assessment。
- secret、credential、customer data、private repository informationが関係する可能性。

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
