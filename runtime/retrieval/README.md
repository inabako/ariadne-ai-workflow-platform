# Runtime Retrieval

`runtime/retrieval/` は、workflow task を順次または並列で処理するときに必要な情報を取り出し、Agentへ渡すための機能を格納します。

## Responsibility

- task queue / task graph を読み取る
- 前工程のartifactを取得する
- `work/<採番ID>/context/*.json` を読み取る
- Agentに必要なhandoff packageを組み立てる
- sequential / parallel task execution を補助する
- task結果を `artifact-index.json` に反映する

## CLI

```powershell
python runtime/retrieval/task_runner.py `
  --work-id WF-20260531-233000 `
  --task-file work/WF-20260531-233000/context/task-plan.json `
  --mode parallel `
  --max-workers 4
```

`--mode sequential` を指定すると、依存関係を見ながら順次実行します。

`--mode parallel` を指定すると、依存関係が満たされたtaskを並列実行します。

`--dry-run` を付けると、実コマンドは実行せず task plan の処理順とreport生成だけを確認できます。

## Retrieval Inputs

- `agent-context.json`
- `artifact-index.json`
- `qa-records.json`
- `finding-records.json`
- `decision-records.json`
- `test-evidence.json`
- `handoff-package.json`
- `work/<採番ID>/design-document/`
- `work/<採番ID>/process-report/`
- `work/<採番ID>/test-specifications/`
- `work/<採番ID>/test-evidence/`

## Execution Model

task は依存関係に応じて、順次または並列で処理します。

- sequential: 前工程の判断やartifactが必要なtask
- parallel: 独立したreview、test planning、documentationなどのtask

## Task Plan Example

```json
{
  "schema_version": "1.0",
  "execution": {
    "mode": "parallel",
    "max_workers": 4
  },
  "tasks": [
    {
      "id": "architecture-review",
      "name": "Architecture Review",
      "depends_on": [],
      "command": ["python", "--version"]
    },
    {
      "id": "safety-review",
      "name": "Safety Review",
      "depends_on": ["architecture-review"],
      "command": ["python", "--version"]
    }
  ]
}
```

## Principle

Agentが毎回すべてを読み直すのではなく、taskに必要な context と artifact を選んで渡します。
