# リリース方針

ARIADNEのreleaseは、review可能で、再現可能で、evidenceに支えられている必要があります。

## バージョン管理

公開releaseではsemantic versioningを使います。詳細は [versioning-policy.md](versioning-policy.md) を参照してください。

## 必須Release材料

- `LICENSE`
- `README.md`
- `CHANGELOG.md`
- `CHANGELOG.en.md`
- `CITATION.cff`
- `SECURITY.md`
- `SECURITY.en.md`
- `CONTRIBUTING.md`
- `CONTRIBUTING.en.md`
- `NOTICE`
- `NOTICE.ja`
- Release checklist
- Release manifest
- Validation output
- Known limitations

## Release Gate

releaseは、human reviewerが次を確認するまでreadyではありません。

- working treeがcleanである。
- testとrelease validationが通っている、または例外が明示的に受容されている。
- license metadataが一貫している。
- 公開文書にsecret、private URL、local absolute path、顧客data、未公開project detailが含まれていない。
- release noteが実装済みbehaviorと一致している。

## License Status

repository licenseは `AGPL-3.0-or-later` です。release前に、`LICENSE`、package metadata、`CITATION.cff`、README、release manifest、第三者license reviewがこの方針と一致していることを確認します。
