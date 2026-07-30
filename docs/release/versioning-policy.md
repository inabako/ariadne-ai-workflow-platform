# バージョン方針

ARIADNEは公開release tagにsemantic versioningを使います。

## Format

- release tagは `vMAJOR.MINOR.PATCH` 形式を使います。例: `v0.1.0`
- pre-release tagでは `v0.1.0-rc.1` のようなsemantic suffixを使えます。
- runtime package versionは、先頭の `v` を除いた同じ数値versionを使います。

## Source of Truth

repository-level version fileを導入するまでは、`runtime/pyproject.toml` をruntime release validation用のmachine-readableなversion sourceとします。

## Development Notes

`docs/development-notes/vX.Y.Z.md` はrepository全体の節目を説明できます。ただし、package metadataやrelease metadataの代替にはしません。
