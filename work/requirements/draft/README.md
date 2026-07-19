# 要件定義草案置き場

このディレクトリには、人間が書いた要件定義の草案を配置します。

ここに置くのは、まだ完成版ではない箇条書きのメモや `.txt` 草案です。

推奨する草案ファイル:

```text
work/requirements/draft/<draft-name>.txt
```

`/requirement-discovery` workflow は、この草案を読み取り、内容を精査します。

情報が不足している場合は、AI が勝手に設計や実装案を決めず、人間へ質問します。

質問と回答を反映したあと、まずレビュー用の要件定義書をこのディレクトリに作成します。

人間レビューで OK になった場合のみ、完成版の要件定義書を以下へ保存します。

```text
work/requirements/
```

未完成の草案を直接 `work/requirements/` に置かないでください。

`work/requirements/` は、後続の intake workflow に渡す完成版の要件定義書を1件だけ置くための場所です。

## 草案に含めたい内容

わかっている範囲で、以下を書いてください。

- Repository
- Target Branch
- 目的
- 現在の挙動
- 目標の挙動
- 安全要件
- STOP / emergency stop behavior
- 通信断時の挙動
- Network
- UI
- Telemetry
- Simulator
- 記事候補
- 将来拡張
- パフォーマンス改善

## Critical 項目

以下が不明な場合は、`unknown` と書いてください。

- Repository
- Target Branch
- 安全要件
- STOP / emergency stop behavior
- 通信断時の挙動

`/requirement-discovery` workflow は、これらを推測せず、必要な質問を人間へ返します。
