---
language: ja-JP
---

# Naming Rules

この文書は、成果物内の file、directory、module、class、function、variable、configuration、schema、artifactの命名方針を定義します。

命名は見た目を揃えるためだけではありません。

人間と AI Agent が、名前から責務、対象、状態、scope を推測しすぎずに理解できる状態を作ります。

## 目的

Naming Rulesの目的は、次を実現することです。

* 名前から責務と意図を読み取れる。
* 同じ概念へ複数の呼び方を使わない。
* 略語や内部用語による認識差を減らす。
* artifact や Evidence を検索しやすくする。
* boilerplate間で基本用語を揃える。

## General Rules

### MUST

* 名前は対象の責務または意味を表す。
* 同じ概念には、原則として同じ用語を使用する。
* 異なる概念へ同じ名前を使用しない。
* 一時的な名前、意味のない連番、曖昧な略語を production artifact へ残さない。
* 名前と実際の挙動が一致しない状態を放置しない。
* security上の秘密情報を file 名、variable 名、artifact 名へ含めない。

### SHOULD

* 短さよりも意味の明確さを優先する。
* project 内で既に定着している用語を優先する。
* domain用語と technology用語を区別する。
* 検索しやすい一貫した語順を採用する。
* 否定形よりも肯定形で状態を表現する。

## Abbreviations

### MUST

* team または repository 内で共有されていない略語を使用しない。
* 一つの略語へ複数の意味を持たせない。
* security、protocol、標準技術名称など、一般的な略語を独自に変形しない。

### SHOULD

* HTTP、URL、ID、APIなど、広く定着している略語は使用できる。
* project 固有略語には docs または glossary を用意する。
* 名前を短くするためだけの母音省略や文字削減を避ける。

## Functions and Operations

### MUST

* function 名は実行する operation を表す。
* side effect を持つ function を、単なる取得に見える名前にしない。
* boolean を返す判定は、判定内容が分かる名前にする。
* create、update、delete、archive、publishなど、mutation を表す語を曖昧にしない。
* async、retry、fallbackなど重要な実行特性を隠さない。

### SHOULD

例:

* `loadContext`
* `validateConfiguration`
* `createProcessReport`
* `isRetryable`
* `hasRequiredEvidence`
* `archiveWorkArtifacts`

避ける例:

* `process`
* `handle`
* `doTask`
* `executeData`
* `check`

ただし、対象 class や module によって意味が明確な場合は、過度に長い名前へしません。

## Variables and Values

### MUST

* variable 名から値の意味を判断できるようにする。
* 単位が重要な値には、秒、分、byte、件数などを明示する。
* boolean は状態または条件として読める名前にする。
* list、map、setなどの collection は、内容が分かる名前にする。
* `data`、`info`、`value`などの汎用名を広い scope で使用しない。

### SHOULD

例:

* `timeoutSeconds`
* `retryCount`
* `artifactPaths`
* `isHumanCheckRequired`
* `selectedRuntime`
* `configurationByEnvironment`

## Files and Directories

### MUST

* directory 名は格納責務を表す。
* 同じ種類の artifact を複数の曖昧な directory へ分散させない。
* `misc`、`tmp`、`other`などを恒久的な格納先にしない。
* archive、generated、evidence、template を識別可能にする。
* filename から文書または artifactの目的を判断できるようにする。

### SHOULD

* directory と fileの命名規則は repository 内で統一する。
* Markdown は原則として kebab-case を使用する。
* machine-readable artifact は schema や既存規則に従う。
* 日時や work-id を付与する場合は共通 format を使用する。

## Configuration

### MUST

* configuration 名から用途と scope が分かるようにする。
* secret と通常設定を同じ prefix や group へ混在させない。
* enable/disable、timeout、limitなどの意味を曖昧にしない。
* environment variable は repository 内で命名規則を統一する。
* deprecatedな名称を残す場合は移行先を明示する。

### SHOULD

* environment variable は大文字 snake case を基本とする。
* boolean設定は肯定形を優先する。
* 単位を名称に含める。
* 外部 toolの公式名称を独自翻訳しすぎない。

## Errors, Logs and Events

### MUST

* error code、event name、metric name は安定した識別子として扱う。
* 人間向け message と machine-readable identifier を混同しない。
* 同じ event へ複数の名称を使用しない。
* success と failure を曖昧な status 名で表現しない。

### SHOULD

* event は過去形または状態変化として表現する。
* command は命令形で表現する。
* metric には対象と単位を含める。
* status は許容値を schema または enum で定義する。

## Schema and Artifact Names

### MUST

* schema 名は対象 domain と versioning方針を表す。
* artifact 名から work、phase、種類を追跡できるようにする。
* UUID や timestampだけで、人間が種類を判断できない状態を避ける。
* filename と内容の種類を一致させる。
* rename 時は参照元、index、RAG metadata への影響を確認する。

## Renaming

### MUST

* rename は見た目の変更ではなく contract 変更として影響を確認する。
* public API、schema、configuration、CLI optionの rename では compatibility を考慮する。
* old name を残す場合は deprecated状態を明示する。
* file移動や rename 後は link、import、script、docs、RAG source を確認する。

## AI Agent 向け規範

AI Agent は新しい名前を作る前に、次を確認します。

1. repository 内の既存用語。
2. glossary、schema、docs。
3. 同じ概念の既存名称。
4. public contract への影響。
5. 検索性。
6. boilerplate間の一貫性。

独自の略語や新しい概念名を無断で増やしません。

## まとめ

* 名前は責務、意図、状態、scope を表す。
* 同じ概念には同じ用語を使う。
* 略語や汎用名による認識負荷を増やさない。
* configuration、event、schema、artifact は安定した contract として扱う。
* rename 時は codeだけでなく docs、schema、RAG、link を確認する。
