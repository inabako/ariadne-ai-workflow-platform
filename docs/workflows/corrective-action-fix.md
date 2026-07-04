# Corrective Action Fix

Corrective Action Report を作成し、RAG build/load、GitHub Issue、remote-first branch作成、修正、test、人間確認、pushまで進めるworkflowです。

## Command

```text
/corrective-action-fix <target-repository> <target-branch> [report]
```

例:

```text
/corrective-action-fix localty-system-gui develop
```

`/corrective-action-report` で作成済みのレポートを使う場合:

```text
/corrective-action-fix localty-system-gui develop rag/corrective-action-report/260704120000_ABC12345_localty-system-gui.md
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
3. `report` が指定されていれば `/corrective-action-report` の出力として読み込む。未指定ならCorrective Action Reportを作る。
4. environment preflightを実行し、不足toolがあればinstall listを出して止まる。
5. `/rag-build` 相当のpipelineでreportをRAG化する。
6. `/rag-load` で開発前contextを読む。
7. 不明な実装領域があれば外部Web RAGをsupporting referenceとしてdispatchする。
8. 専門知識がIssue scope / 実装方針 / test specificationに影響する場合はSpecialist Agent reviewを実行する。
9. support repository / tool / packageの必要性を確認する。
10. GitHub Issue draftを作る。
11. 人間承認後にGitHub Issueを作成する。
12. GitHub上に `feature/issue-<issue-number>` を作り、`work/issue-<issue-number>` にcloneする。
13. encoding / mojibake gateを確認する。
14. `work/requirements/svg-input/FIX_*.svg`がある場合、Issue作業領域へ取り込み、GaC / UaC GUI ModeをFIX modeで実行する。
15. Next.js画面機能を含む場合、Next.js Webapp Implementation Prepを実行する。
16. `work/requirements/svg-input/WEB_FIX_*.svg`がある場合、Web SVG Layout Modeを実行する。
17. corrective fixを実装する。
18. test specificationとtest evidenceを残す。
19. PyQt / Qt GUIの場合、テストケース表を元にQTest結合テストをソース化する。
20. startup / integration checkとhuman check gateを通す。
21. PR材料とknowledge capture packageを作る。
22. 人間承認後にIssue branchへpushする。
23. Issue titleをPR titleとして `develop` へPull Requestを作成する。

## GaC / UaC GUI Mode

`work/requirements/svg-input/FIX_*.svg`が存在する場合、`work/issue-<number>/input/gui/`へ取り込み、論理Issue ID `FIX-<number>`と`--mode corrective-improvement`を使って[GaC / UaC GUI Mode](gui-mode.md)を実行します。

生成物は改善候補です。最小変更、既存挙動維持、固定座標排除、Widget責務分離、QTest回帰防止を確認し、必要な差分だけを既存sourceへ取り込みます。

## Next.js Webapp Implementation Prep

改善対象にNext.js dashboard / admin / monitoring / business webapp画面が含まれる場合、source変更前に[Next.js Webapp Implementation Prep](nextjs-webapp-implementation-prep.md)を実行します。

出力:

```text
work/issue-<issue-number>/process-report/nextjs-webapp-implementation-prep.md
```

既存Next.js appでは `nextjs-webapp-template` はreference-onlyです。route、user action、API contract、auth/session、env/secret境界、typecheck、lint、unit、e2e、health、UI smoke、API connectivityが未整理なら実装へ進みません。

## Web SVG Layout Mode

改善対象にNext.js画面が含まれ、`work/requirements/svg-input/WEB_FIX_*.svg` が存在する場合、`work/issue-<number>/input/web-ui/` へ取り込み、[Web SVG Layout Mode](web-svg-layout-mode.md)を実行します。

出力:

```text
work/issue-<issue-number>/web-ui/
```

生成されたReact / Playwright候補は、既存画面の最小修正、既存挙動維持、回帰防止の観点でreviewし、採用部分だけsourceへ統合します。

## External Web RAG Support

外部Web RAGは、不明な実装領域や公式仕様確認が必要な箇所のsupporting referenceとして使います。

```text
corrective action report
  -> RAG build/load
  -> external-web RAG dispatch for unknown implementation areas
  -> Issue bodyにsupporting referenceと未確認事項を書く
  -> implementation
  -> tests / evidence
  -> human check
```

使う例:

- Go realtime gateway
- UDP / TCP / QUIC behavior
- NAT traversal
- GStreamer pipeline behavior
- Docker / Windows / Raspberry Pi platform behavior
- Prometheus / OpenTelemetry design

外部WebRAGは、実装方針、test specification、risk checkを補助します。

ただし、採用した挙動はlocal test、integration evidence、human checkで確認します。

## Specialist Review Gate

Corrective Action Fixでは、外部Web RAGを読んだあと、専門知識が実装判断に影響する場合にSpecialist Agent reviewを挟みます。

review対象:

- Issue scope
- implementation plan
- test specification
- safety / security / network / observability review
- startup / integration check plan

review結果は次に保存します。

```text
work/<target-branch>/process-report/specialist-review-<domain>.md
work/issue-<issue-number>/process-report/specialist-review-<domain>.md
```

Specialist Agentは、次を明示します。

- 採用した内部RAG
- 採用した外部Web RAG
- 信じなかった、または条件付きにした外部claim
- current source code / test evidenceとの整合
- 追加すべきtest case
- unresolved QA / human check item

High / critical finding が残る場合、implementationまたはpushへ進めません。

完了後、review結果は [Knowledge Capture](knowledge-capture.md) でRAG候補として抽出します。

## Issue Body Template

Issue title は、改善フローでは次のprefixを付けます。

```text
[改善フロー] <issue-title>
```

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
- Pull Request 作成
- RAG登録
- report-only close archive準備 / prune

## Pull Request Flow

Issue branchへpushした後、`develop` にPull Requestを送信します。

```text
feature/issue-<issue-number>
  -> push
  -> Pull Request to develop
```

Pull Request title は、GitHub Issue titleを使用します。

Pull Request body には変更点のMermaid式sequence diagramを含めます。

## PyQt QTest Integration Source Gate

対象repositoryがPyQt / Qt GUIを含む場合、test specificationのテストケース表からQTest化できる結合疎通試験をソース化します。

```text
test specification
  -> PyQt QTest Source Plan
  -> src/tests/qt/test_<feature>_integration.py
  -> QTest execution evidence
  -> remaining human check
```

QTest化する例:

- Connect button / Disconnect button
- control key send
- telemetry receive display
- sensor override UI
- Event Log / Packet display
- FPS label / video state label
- show / close lifecycle
- external I/O disabled or stubbed startup

QTest化しない、または人間確認を残す例:

- 実robot motion
- 実cameraの画質確認
- physical STOP
- router / VPN / field network
- timingが安定化できない実機挙動

QTestソースは、承認済みテスト仕様書のTest Case IDに紐づけます。

推奨保存先:

```text
work/issue-<issue-number>/source/repository/src/tests/qt/test_<feature>_integration.py
```

テスト証跡は次に保存します。

```text
work/issue-<issue-number>/test-evidence/qtest_integration/
work/issue-<issue-number>/source/repository/docs/evidence/issue-<issue-number>/integration/qtest/
```

テスト仕様書、unit test、manual integration、human checkを含む全体の保存先は [Test Artifact Storage](../reference/test-artifact-storage.md) に従います。
Knowledge Capture実行時にtarget repository側の証跡フォルダは自動生成されますが、scaffold用 `README.md` だけではpush可能な証跡とはみなしません。

## Guardrails

- 外部WebRAGは current source code、test evidence、corrective action report、人間承認済みfindingを上書きしません。
- 外部Web由来の修正方針は、test evidenceで確認してから採用します。
- Issue bodyとtest specificationには、外部WebRAGを使った箇所と未確認事項を残します。
- Specialist Agent reviewで採用した外部知識は、どのtest evidenceまたはhuman checkで検証したかを残します。
- PyQt QTestは、承認済みテストケース表にない挙動を勝手に仕様化しません。
- QTestで実UDP、GStreamer、RobotController、hardware serviceを起動する場合は、テストケース表に明示し、通常はstub / disable方針を優先します。

## Source Skill

```text
skills/corrective-action-fix/SKILL.md
```
