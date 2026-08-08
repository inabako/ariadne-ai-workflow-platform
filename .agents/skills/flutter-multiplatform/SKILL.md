---
name: flutter-multiplatform
description: Use when a workflow must create, modify, analyze, test, or build a Flutter application for Android, iOS, Web, Windows, macOS, or Linux while preserving target-platform selection, environment dispatch, evidence, and Context First handoff.
---

# Flutter Multi-platform Workflow

このSkillは、Flutterアプリケーションの新規作成、既存改修、対象platform追加、platform別test/build計画を扱います。

## 基本原則

- Flutter targetは推測で全platformにしない。
- `work/<work-id>/requirements/flutter-targets.yaml` または `aiwfctl flutter ... --targets` を確認する。
- 未指定ならHuman Checkで止める。
- buildや配布より前に、対象platform、host OS、Flutter SDK、署名、native依存、実機確認の要否を明示する。
- sourceを無条件に上書きしない。boilerplateはwork配下へ展開し、review後に採用する。

## Runtime entrypoint

通常は親workflowから次を呼びます。

```powershell
aiwfctl env select flutter --work-id <work-id>
aiwfctl flutter analyze --work-id <work-id>
aiwfctl flutter init --work-id <work-id> --targets android,web,windows
aiwfctl flutter verify --work-id <work-id> --execute
aiwfctl flutter build --work-id <work-id> --targets web --mode debug --execute
aiwfctl flutter finalize --work-id <work-id>
```

全体をまとめる場合:

```powershell
aiwfctl flutter run-workflow --work-id <work-id> --targets android,web,windows --execute
```

`--execute` を付けない場合は計画とContext生成だけを行います。実試験を行う場合は、必ず `--execute` を明示します。

release buildを実行する場合は、署名・配布・成果物公開の判断が絡むため、次のようにHuman Check承認を明示します。

```powershell
aiwfctl flutter build --work-id <work-id> --targets web --mode release --execute --human-check approved
```

## 対象platform

利用可能なtarget:

- `android`
- `ios`
- `web`
- `windows`
- `macos`
- `linux`

host OSごとのbuild可否:

- Android / Web: Windows / macOS / Linux
- iOS / macOS: macOS
- Windows: Windows
- Linux: Linux

現在hostでbuildできないtargetは `build_environment_required` または `remote_build_required` として扱います。

## Human Check

次は必ずHuman Checkです。

- 対象platform未指定
- minimum OS version
- iOS / macOS signing
- Android signing
- Store配布
- Platform Channel追加
- native code追加
- release build
- 実機試験が必要な機能
- security上の重要判断

## 成果物

- `work/<work-id>/context/flutter-development-context.json`
- `work/<work-id>/context/context-manifest.json`
- `work/<work-id>/reports/flutter-multiplatform-report.md`
- `work/<work-id>/evidence/flutter/common/verification-plan.md`
- `work/<work-id>/evidence/flutter/**/<command>-summary.md`
- `work/<work-id>/evidence/flutter/finalization-summary.md`
- `work/<work-id>/implementation/flutter-project/`

## Knowledge化

生成source全体をそのままKnowledge化しません。対象は次に限定します。

- target platform判断
- build環境判断
- platform差分
- test方法
- build error解決
- UI / permission / native dependency上の注意

## Workflow Feedback Output

Flutter workflow中に、対象platform判断、Flutter SDK導入、host OS制約、boilerplate不足、Platform Channel、test/build evidence、docs不足で摩擦が出た場合は、通常workflowの成果物とは別に `work/feedback/` へFeedback report候補を保存します。

Feedback reportには `Review Status: Proposed` を含めます。

Do not run `/self-improvement` automatically from this workflow. Feedbackが蓄積した後、人間が `/self-improvement` を選んだ場合に採用 / 不採用 / 保留を判断します。
