---
name: noise-reduction-phase
description: 要件定義段階で未知用語、表記揺れ、資料矛盾、曖昧表現、AIが推測しそうな箇所、業務ルール不足を抽出し、Human InterviewとProject Glossaryを作成します。
argument-hint: "<draft-stem>"
agent: agent
---

# Noise Reduction Phase

このpromptは独立した大本流ではありません。`/requirement-discovery` の中で、要件review draftを作る前に差し込む準備サブフローです。

目的は、設計や実装を始めることではありません。人間とAIの認識齟齬、ハルシネーション、手戻り、レビュー工数、クレジット消費を減らすために、資料内のノイズを先に取り除きます。

## 入力

- 要件草案
- 要件定義書
- 基本設計書、詳細設計書
- API仕様書、OpenAPI
- ER図、シーケンス図、ADR
- 業務フロー
- RAG context
- Glossaryが存在する場合はGlossary

入力資料はpathで追跡できるものを優先します。会話中の説明だけで確定扱いにせず、参照元を各reportへ残してください。

## 出力

```text
work/requirements/draft/<draft-stem>-noise-reduction/
```

必須成果物:

```text
unknown-words-report.md
terminology-conflict-report.md
terminology-alias-report.md
document-conflict-report.md
ambiguous-language-report.md
ai-confusion-report.md
missing-definition-report.md
human-interview-sheet.md
project-glossary.md
readiness-report.md
```

## 流れ

1. 資料全体と資料同士の関係を読む。設計・実装は開始しない。
2. プロジェクト固有用語を抽出する。
3. 一般知識との衝突を検出する。
4. 表記揺れ、略称、同義語候補を検出する。
5. 資料間の矛盾を検出する。
6. 曖昧な日本語を検出する。
7. AIが推測しそうになった箇所を抽出する。
8. 業務ルール不足を抽出する。
9. Human Interview票を作成する。
10. Project Glossaryを作成する。
11. Readinessを `PASS`、`WARNING`、`BLOCK` のいずれかで評価する。

## Readiness

- `PASS`: 設計開始可能。Human Interviewに設計阻害項目がない。
- `WARNING`: 軽微な確認あり。未解決項目をOpen Questionsへ残せば要件reviewへ進める。
- `BLOCK`: Human Interview完了まで設計、実装、完成版要件化を禁止する。

## 停止条件

- High優先度のHuman Interview質問が未回答。
- 用語衝突や表記揺れでAPI、DB、状態、イベントの意味が確定できない。
- 資料矛盾でscope、状態遷移、異常系、rollback、timeout、retryが決まらない。
- AI Confusion Reportに、推測なしでは要件文を書けない項目が残っている。
- Missing Definition Reportに、実装やテスト条件を左右する業務ルール不足が残っている。

## 守ること

- 推測しない。
- 一般知識で補完しない。
- 分からないことは不明とする。
- Human Interviewを必ず生成する。
- 用語統一を優先する。
- 暗黙知を可視化する。
- 資料矛盾を放置しない。
- `BLOCK` の場合は `/requirement-discovery` を完成扱いにしない。
