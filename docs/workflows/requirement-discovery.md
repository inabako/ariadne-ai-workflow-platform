# Requirement Discovery

箇条書きの草案から、開発workflowへ渡せる完成版の要件定義書を作るworkflowです。

## Command

```text
/requirement-discovery
```

## Input

草案は次の場所に置きます。

```text
work/requirements/draft/
```

例:

```text
work/requirements/draft/localty-gui-smoke-test.txt
```

## Output

人間レビューでOKになった完成版だけを次へ進めます。

```text
work/requirements/<completed-requirements>.md
```

## Flow

1. `work/requirements/draft/` の草案を読む。
2. blocking clarification があれば質問する。
3. 必要ならRAG contextを補助的に読む。
4. review draftを作る。
5. 人間OK後に `work/requirements/` へ完成版を保存する。

## Gate

次の項目が不足している場合は、開発workflowへ進めません。

- 対象repository
- target branch
- 変更intent
- safety / rollback / test / evidence の最低限の判断材料
- `Repository Control`

## Next

- 新規systemなら [Robotics New System](robotics-new-system.md)
- 既存systemの変更なら [Robotics Feature Maintenance](robotics-feature-maintenance.md)
