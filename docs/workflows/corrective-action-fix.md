# Corrective Action Fix

Corrective Action Report を作成し、RAG build/load、GitHub Issue、remote-first branch作成、修正、test、人間確認、pushまで進めるworkflowです。

## Command

```text
/corrective-action-fix <target-repository> <target-branch>
```

例:

```text
/corrective-action-fix localty-system-gui develop
```

## Directory Model

```text
work/<target-branch>/source/repository
work/issue-<issue-number>/source/repository
```

Git branch は次の形式にします。

```text
feature/issue-<issue-number>
```

## Flow

1. `work/<target-branch>` を初期化する。
2. target branchをbase checkoutへ取得する。
3. Corrective Action Reportを作る。
4. environment preflightを実行し、不足toolがあればinstall listを出して止まる。
5. `/rag-build` 相当のpipelineでreportをRAG化する。
6. `/rag-load` で開発前contextを読む。
7. support repository / tool / packageの必要性を確認する。
8. GitHub Issue draftを作る。
9. 人間承認後にGitHub Issueを作成する。
10. GitHub上に `feature/issue-<issue-number>` を作り、`work/issue-<issue-number>` にcloneする。
11. encoding / mojibake gateを確認する。
12. corrective fixを実装する。
13. test specificationとtest evidenceを残す。
14. startup / integration checkとhuman check gateを通す。
15. PR材料とknowledge capture packageを作る。
16. 人間承認後にpushする。

## Issue Body Template

Issue body は次の優先順位で選びます。

1. 明示された `--body-file`
2. target repository の `.github/ISSUE_TEMPLATE.md`
3. `runtime/github/issue_manager.py` のfallback本文

target repository templateを使う場合、`Report`、`Target branch`、`Target commit` はworkflow contextから補完します。

## Human Gates

- GitHub Issue 作成
- missing tool のinstall
- startup / integration check
- push
- RAG登録
- archive移動

## Source Skill

```text
skills/corrective-action-fix/SKILL.md
```
