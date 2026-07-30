# Release Checklist

## Source

- [ ] working treeがcleanである。
- [ ] target branchが最新である。
- [ ] versionが更新されている。
- [ ] tagとversionが一致している。
- [ ] secretが含まれていない。
- [ ] private URLが含まれていない。
- [ ] 顧客固有情報が含まれていない。
- [ ] 非公開project情報が含まれていない。

## Tests

- [ ] unit testが通っている。
- [ ] integration testが通っている、または対象外として文書化されている。
- [ ] static analysisが通っている、または例外が文書化されている。
- [ ] coverageがreviewされている。
- [ ] critical workflowが実行されている。
- [ ] retryとresume behaviorが検証されている。
- [ ] evidenceがreviewされている。

## Documentation

- [ ] READMEが最新である。
- [ ] architecture documentが最新である。
- [ ] command referenceが最新である。
- [ ] CHANGELOGが最新である。
- [ ] CHANGELOG.en.mdが最新である。
- [ ] CITATION.cffが最新である。
- [ ] CONTRIBUTING.md / CONTRIBUTING.en.mdが最新である。
- [ ] SECURITY.md / SECURITY.en.mdが最新である。
- [ ] NOTICE / NOTICE.jaが最新である。
- [ ] license情報が最新で、内部的に一貫している。
- [ ] known limitationsが文書化されている。

## Release

- [ ] release manifestが生成されている。
- [ ] checksumが生成されている。
- [ ] Git tagが作成されている。
- [ ] GitHub Releaseが作成されている。
- [ ] release noteがreviewされている。
- [ ] release assetがuploadされている。
- [ ] commit hashが記録されている。

## Post-release

- [ ] release pageが確認されている。
- [ ] source archiveをdownloadできる。
- [ ] documentation linkが機能している。
- [ ] citation情報が正しく表示されている。
- [ ] 次のdevelopment versionが準備されている。
