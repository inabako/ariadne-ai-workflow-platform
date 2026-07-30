# /flutter-multiplatform

Flutterアプリケーションを扱うときは、対象platformを先に確定し、環境選択、boilerplate、test、build dispatch、evidence、Context First handoffを順に確認する。

## 手順

1. `work/<work-id>/requirements/flutter-targets.yaml` または人間指定の `--targets` を確認する。
2. 対象platformが未指定なら全platform対応と推測せずHuman Checkで止める。
3. `aiwfctl env select flutter --work-id <work-id>` を実行し、Flutter profileをContext Firstへ登録する。
4. `aiwfctl flutter analyze --work-id <work-id>` で既存Flutter project、host OS、target別build可否を確認する。
5. 新規構成が必要なら `aiwfctl flutter init --work-id <work-id> --targets ...` でwork配下にboilerplateを展開する。
6. `aiwfctl flutter verify --work-id <work-id>` で静的解析・test計画とevidenceを作る。実試験まで行う場合は `--execute` を付ける。
7. `aiwfctl flutter build --work-id <work-id> --targets ... --mode <mode>` でtarget別build dispatchを作る。実buildまで行う場合は `--execute` を付ける。
8. `aiwfctl flutter finalize --work-id <work-id>` で保存済みverify/build/evidenceを読み、完了判定を作る。
9. `flutter-development-context.json` と `flutter-multiplatform-report.md` を後続workflowへ渡す。

## 禁止

- target未指定時にAndroid/iOS/Web/Desktop全部とみなす。
- signing credentialやStore配布設定を自動生成する。
- Platform Channelやnative codeをHuman Checkなしに追加する。
- 既存project構成を無視してboilerplateをtarget sourceへ直接上書きする。
- `--execute` なしに実試験・実buildを行ったものとして完了判定する。
