# RAG Dispatcher Design Notes

この文書は、RAG dispatcher の設計思想、Agent間で共有するノウハウ、運用上の判断基準をまとめます。

RAG dispatcher は単なる検索CLIではありません。
後続Agentへ「何を、なぜ、どの条件で検索したか」を渡すための意図継承装置です。

## 基本思想

RAG artifact のファイル名は UUID です。
そのため、UUIDを検索入口にしません。

このrepositoryでは、次の分離を守ります。

```text
意味で探す
  content / metadata / semantic hint / embedding

UUIDで記録する
  dispatch plan / retrieval result / context pack / dispatch aggregate
```

この分離により、検索品質と証跡管理を混ぜずに済みます。

## Dispatcher の責務

`runtime/rag/rag_dispatcher.py` は、次の責務だけを持ちます。

- task / context / work-dir から検索計画を作る
- `rag-dispatch-plan` を保存する
- queryを複数に分けて `retrieve_context.py` を並列実行する
- 生成された `rag-context-pack` を集約する
- `rag-load-dispatch` を保存する

一方で、次は dispatcher の責務ではありません。

- source report の正規化
- chunk作成
- embedding index作成
- raw RAG本文の丸ごと持ち回り
- safety-critical判断の最終確定
- repository evidence の代替

## 標準フロー

```text
Intent / Task
  ↓
Metadata filter
  repository / branch / project / tag / source_type / category / trust_level
  ↓
Semantic Hint
  component / safety / test gap / docs gap / operation risk
  ↓
rag-dispatch-plan
  ↓
retrieve_context.py をqueryごとに並列実行
  ↓
keyword / semantic / hybrid scoring
  ↓
rag-retrieval-result
  ↓
rag-context-pack
  ↓
rag-load-dispatch
  ↓
後続Agentがplanとcontext packを読む
```

重要なのは、検索前の判断と検索後の結果を分けることです。

| Artifact | 役割 |
| --- | --- |
| `rag-dispatch-plan` | 検索前の意図、metadata、semantic hint、query、purpose、stop condition |
| `rag-retrieval-result` | queryごとの候補、選択chunk、除外chunk、score |
| `rag-context-pack` | Agentに渡す圧縮済みcontextとsource |
| `rag-load-dispatch` | 複数context packの集約結果 |

## rag-dispatch-plan が持つ価値

`rag-dispatch-plan` は、検索前の判断を固定する成果物です。

これにより、後続Agentは次を確認できます。

- どのIntentから検索したか
- どのmetadata filterで絞ったか
- どのsemantic hintを使ったか
- なぜそのqueryが必要だったか
- どのstop conditionを意識していたか
- 既存planを再利用したのか、新規生成したのか

これは検索品質だけでなく、説明可能性と再現性を上げます。

## Query planning の観点

queryは単語の羅列ではなく、目的を持つ検索単位として扱います。

代表的な観点:

- target repository / branch の過去知見
- component責務境界
- safety / STOP / communication loss
- startup / shutdown / rollback
- telemetry / watchdog / observability
- test gap / regression / smoke / integration
- documentation gap / operations / README
- external-web category / trust level

良いqueryは、次の形に近いです。

```json
{
  "query": "TelemetryService Watchdog test gap",
  "purpose": "component test and regression risk",
  "search_mode": "hybrid",
  "filters": {
    "repository": "localty-system-gui",
    "branch": "develop",
    "tags": ["workflow"]
  }
}
```

## Metadata filter の使い方

metadata filter は、検索範囲を狭めるための重要な制御です。

| Filter | 用途 |
| --- | --- |
| `repository` | 対象repositoryの知見へ寄せる |
| `branch` | 対象branchの文脈へ寄せる |
| `project` | project横断RAGを絞る |
| `tag` | workflow、safety、testなどの観点で絞る |
| `source_type` | internal-work / external-web などを分ける |
| `category` | external-webのnetwork、platform、videoなどを絞る |
| `trust_level` | 外部知識の信頼度で絞る |

metadataが分かっている場合は、曖昧なsemantic searchに任せすぎない方が安定します。

## Search mode の考え方

| Mode | 向いている場面 |
| --- | --- |
| `keyword` | 固有名詞、ファイル名、class名、明確な用語 |
| `semantic` | 表現揺れが大きい概念探索 |
| `hybrid` | 通常運用の標準 |

通常は `hybrid` を使います。
このrepositoryのembeddingはlocal sparse embeddingなので、外部providerに依存しないdeterministic baselineとして扱います。

## UUID の扱い

UUIDは検索入口ではなく、証跡と再読込のハンドルです。

やってよいこと:

- `rag-load-dispatch` から `dispatch_plan` を読む
- `rag-load-dispatch` から `context_pack` を読む
- `rag-context-pack` の `sources` で根拠chunkを追跡する
- `rag-retrieval-result` で除外理由を確認する

避けること:

- UUID名から意味を推測する
- UUID順で重要度を判断する
- ファイル名検索だけでRAGを読む

## Agent間 handoff

後続Agentは、RAG contextを読む前に dispatch plan を確認します。

推奨順序:

1. `rag-load-dispatch` を開く
2. `dispatch_plan` を開く
3. planの `intent` / `metadata` / `semantic_hints` / `queries` を確認する
4. `context_packs` を開く
5. context pack の `sources` を確認する
6. 現在のrepository evidenceと矛盾しないか確認する
7. 必要なら追加query planを作る

RAGは補助contextです。
current repository evidence、human answer、safety gateを上書きしません。

## 既存planの再利用

同じIssue内で複数Agentが同じ意図のRAGを読む場合、既存の `rag-dispatch-plan` を再利用できます。

```powershell
python runtime/rag/rag_dispatcher.py `
  --dispatch-plan db/rag/retrieval/<plan-uuid>.json `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000
```

再利用に向いている場面:

- architect、tester、documentation agent が同じIssue文脈を共有する
- corrective-action-fix中に実装前reviewとtest設計で同じRAG前提を使う
- external-web RAGのcategoryとtrust条件を固定したい

再利用しない方がよい場面:

- Intentが変わった
- target repository / branch が変わった
- safety-criticalな新情報が出た
- query不足が明らかになった

## Stop condition

dispatcherは検索を補助しますが、次の場合は後続flowで止めます。

- RAG index / embedding index がない
- safety-criticalな過去findingが現在taskに関係する
- STOP / communication loss / safe state が未定義
- RAGだけではCritical itemを確定できない
- current repository evidenceとRAGが矛盾する
- external-web claimが古い、またはverify-before-useになっている

## Anti-pattern

避けるべき運用:

- queryだけを会話で渡し、planを残さない
- context packだけを読み、dispatch planを読まない
- raw RAG本文を大量に後続Agentへ渡す
- external-web RAGでrepository evidenceを上書きする
- UUIDファイル名に意味を持たせる
- metadata不足のsource reportを増やし続ける
- safety / STOP / communication loss をRAG推測で決める

## 実装上の入口

標準入口:

```powershell
python runtime/rag/rag_dispatcher.py `
  --task "<task summary>" `
  --repository "<target-repository>" `
  --branch "<target-branch>" `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000 `
  --jobs 4
```

single query debug:

```powershell
python runtime/rag/retrieve_context.py `
  "<query>" `
  --search-mode hybrid `
  --top-k 5 `
  --max-chars 4000
```

`retrieve_context.py` はdebug用の単発検索として使い、通常は dispatcher から呼び出します。

## 関連ファイル

| Path | 役割 |
| --- | --- |
| `runtime/rag/rag_dispatcher.py` | query planning、parallel retrieval、aggregate |
| `runtime/rag/retrieve_context.py` | scoring、chunk選択、context pack生成 |
| `.github/schemas/rag-dispatch-plan.schema.json` | dispatch plan schema |
| `.github/schemas/rag-retrieval-result.schema.json` | retrieval result schema |
| `.github/schemas/rag-context-pack.schema.json` | context pack schema |
| `skills/rag-load/SKILL.md` | RAG読み込みskillの実行手順 |
| `docs/reference/rag.md` | RAG全体のpipeline |

## 判断のまとめ

dispatcherの強さは、検索そのものよりも責任分離にあります。

```text
Intentをplanにする
意味で検索する
必要なcontextだけ圧縮する
UUIDで証跡化する
後続Agentへ理由ごと渡す
```

この流れを守ると、Agentは「何となく過去知識を読んだ」のではなく、
「このIntentに対して、この条件で、この理由のqueryを実行した」と説明できます。

これが、本質作業へ集中するためのdispatcher運用です。
