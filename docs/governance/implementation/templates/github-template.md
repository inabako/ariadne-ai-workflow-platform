---
language: ja-JP
---

# GitHub Template

この文書は、GitHub を利用する repository template に必要な構成と規範を定義します。

対象には次を含みます。

* repository初期構成。
* Issue template。
* Pull Request template。
* workflow。
* label。
* branch運用。
* security設定。
* release。
* contribution guide。
* CODEOWNERS。

## 目的

* repository運用の入口を標準化する。
* Issue、Branch、Pull Request、Evidence を接続する。
* review と Human Check を維持する。
* automated workflowの権限を最小化する。
* secret や危険な operation を安全に扱う。
* generated repository が GitHub上で迷わず運用できるようにする。

## Required Structure

必要に応じて次を生成します。

```text
.github/
├── ISSUE_TEMPLATE/
│   ├── feature.yml
│   ├── bug.yml
│   ├── improvement.yml
│   └── config.yml
├── PULL_REQUEST_TEMPLATE/
│   ├── pull_request_template.md
│   └── pull_request_template_ja.md
├── workflows/
├── CODEOWNERS
├── dependabot.yml
└── SECURITY.md
```

repository root には必要に応じて次を配置します。

```text
README.md
CONTRIBUTING.md
SECURITY.md
LICENSE
CODE_OF_CONDUCT.md
```

## Repository Settings

### MUST

template利用時に次を確認します。

* default branch。
* branch protection。
* required review。
* required status check。
* force push restriction。
* deletion restriction。
* merge method。
* secret scanning。
* dependency alert。
* workflow permission。
* private または public classification。

repository visibility 変更は Human Check 対象とします。

## Issue Templates

### MUST

Issue template には、種類に応じて次を含めます。

* purpose。
* background。
* scope。
* non-scope。
* acceptance criteria。
* risk。
* affected artifacts。
* test expectation。
* Human Check requirement。
* Evidence expectation。

bug report には次を追加します。

* actual behavior。
* expected behavior。
* reproduction。
* environment。
* impact。
* log または Evidence location。

### SHOULD

* feature、bug、improvement、security を分離する。
* free-form Issue を完全禁止しない。
* label を自動付与する。
* secret を貼り付けない注意書きを設ける。

## Pull Request Template

### MUST

PR template には次を含めます。

* related Issue。
* intent。
* changes。
* scope。
* non-scope。
* verification。
* test result。
* security impact。
* configuration change。
* migration。
* rollback。
* Human Check。
* Evidence。
* residual risk。

### SHOULD

checkboxだけで完了判定せず、必要な説明欄を用意します。

## Branch Rules

### MUST

* default branch へ直接 push しない運用を基本とする。
* branch 名から purpose または Issue を追跡可能にする。
* long-lived branch を無秩序に増やさない。
* stale branchの扱いを定義する。
* protected branchの rule 変更を Human Check 対象とする。

例:

```text
feature/issue-123-short-description
fix/issue-456-short-description
maintenance/issue-789-short-description
```

## GitHub Actions

### MUST

* action version を commit SHA または信頼可能な version へ固定する。
* workflow permission を最小化する。
* secret を log へ出力しない。
* fork からの workflow 実行で secret を渡さない。
* `pull_request_target` の利用 risk を確認する。
* untrusted input を shell command へ直接渡さない。
* production deployment に Human Check または environment protection を適用する。
* workflow failure を無視しない。

### SHOULD

workflow を責務別に分けます。

```text
ci.yml
security.yml
release.yml
docs.yml
dependency-review.yml
```

## Workflow Permissions

### MUST

default permission は read-only を基本とし、workflow単位で必要な権限だけを付与します。

例:

```yaml
permissions:
 contents: read
```

write permission が必要な場合は、理由を明確にします。

## Secrets

### MUST

* secret を workflow file へ記載しない。
* repository、environment、organization secretの scope を選択する。
* production secret は protected environment で管理する。
* secret 名から値を推測できる情報を含めすぎない。
* secret rotation を可能にする。
* secret を PR comment や artifact へ出力しない。

## CODEOWNERS

### SHOULD

security、workflow、governance、deploymentなど、重要領域に owner を設定します。

例:

```text
/.github/workflows/ @platform-maintainers
/governance/ @governance-maintainers
/infrastructure/ @infrastructure-maintainers
```

CODEOWNERSだけで authorization を保証しません。

## Dependency Management

### SHOULD

* dependency update tool を導入する。
* major update を自動 merge しない。
* security update を優先する。
* update frequency を repository特性に合わせる。
* lock file 更新を含める。
* dependency review を PR で実行する。

## Release

### MUST

* release source を tag または commit で追跡可能にする。
* build artifact と source revision を対応付ける。
* release note を生成または記載する。
* production publish を Human Check 対象とする。
* release artifact へ secret を含めない。
* rollback または previous version を特定可能にする。

## Security Reporting

### MUST

security issue を通常 Issue へ公開しない導線を用意します。

`SECURITY.md` には次を含めます。

* supported versions。
* reporting method。
* response policy。
* disclosure policy。
* prohibited content。

## Template Validation

### MUST

GitHub template を検証する際は、次を確認します。

* YAML syntax。
* workflow permission。
* action version。
* secret reference。
* branch name。
* required file。
* Issue form schema。
* PR template。
* broken link。
* generated repository での CI 実行。

## AI Agent 向け規範

AI Agent は GitHub構成変更時に次を確認します。

1. repository visibility。
2. branch protection。
3. workflow permission。
4. secret。
5. untrusted input。
6. production deployment。
7. CODEOWNERS。
8. Issue と PRの接続。
9. Evidence。
10. Human Check。

## まとめ

* GitHub template は repository運用と reviewの入口を標準化する。
* Issue、PR、test、Evidence を接続する。
* Actions permission を最小化する。
* production release と repository 公開には Human Check を適用する。
* untrusted PR や workflow input から secret と repository を守る。
