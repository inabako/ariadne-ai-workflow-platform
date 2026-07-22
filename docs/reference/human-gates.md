# Human Gate Registry

この文書は、人間承認なしで進めない操作をまとめます。

責任分離を明確にするため、実体ファイルと構造定義ファイルは分けます。

```text
db/registries/registry.duckdb
```

上記はruntimeが読むregistry実体です。ここには承認ゲートの一覧だけを置きます。
`$schema` や `schema_version` は置かず、registry自体の版は `registry_version` で表します。

```text
.github/schemas/human-gates.schema.json
```

上記はregistry実体を検査するためのJSON Schemaです。schema責務は `.github/schemas/` に閉じ込めます。

確認CLI:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . human-gate list
uv run --project runtime python runtime/ctl/ctl.py --repo-root . human-gate check --gate close-prune --human-check approved
```

## 承認が必要な操作

| Gate ID | 操作 | 理由 |
| --- | --- | --- |
| `github-issue-create` | GitHub Issue作成 | 外部GitHub状態を変更するため |
| `branch-create` | branch作成 | Git履歴と作業基点を変更するため |
| `push` | push | remote repositoryへ変更を送信するため |
| `pull-request-create` | Pull Request作成 | GitHub上のreview対象を作成するため |
| `rag-register` | RAG登録 / rebuild | 将来のAI判断に影響する知識を蓄積するため |
| `close-prune` | close archive prune | 作業実体やcacheを削除するため |
| `work-delete` | work削除 | ローカル作業証跡を削除するため |
| `tool-install` | tool / package install | ローカル環境へ変更を加えるため |
| `external-io-test` | 実機 / 外部I/Oテスト | 実機、network、camera、field environmentへ影響する可能性があるため |

## 運用ルール

- 承認値は原則 `approved` とします。
- `削除承認` などの会話上の承認は、実行CLIでは `--human-check approved` として記録します。
- 承認が必要な操作をruntimeへ追加した場合は、この文書、`db/registries/registry.duckdb`、必要に応じて `.github/schemas/human-gates.schema.json` を同時に更新します。
- schema責務の混在を避けるため、`registry.duckdb` の `human_gates` registry payload には `$schema` と `schema_version` を置きません。
- `workflow_doctor.py` はこの責任境界を検査します。
