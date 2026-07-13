# Runtime Intake

`runtime/intake/` は、投入された要件定義書を受付ID単位の作業領域へ移動し、workflow の初期状態を作るための機能を格納します。

## Responsibility

- 受付IDを採番する
- `work/requirements/` の完成版要件定義書を受け付ける
- `work/<採番ID>/` を作成する
- 成果物ディレクトリを初期化する
- 投入された要件定義書を受付ID配下へ移動する
- 初期 `context/*.json` を作成する
- 要件定義書が無い、または `Repository Control` が読めない場合は受領拒否する

## CLI

標準運用では、完成版の要件定義書を `work/requirements/` に配置してから、引数なしで intake します。

```powershell
python runtime/intake/intake_requirements.py `
  --project-name localty-system-gui `
  --workflow ariadne-new-system-development
```

`--workflow` は以下を受け付けます。

```text
ariadne-new-system-development
ariadne-feature-maintenance-development
ariadne-new-system-iac
realtime-iac
```

採番prefixの既定値:

- `ariadne-new-system-development`, `ariadne-new-system-iac`: `SYS-*`
- `ariadne-feature-maintenance-development`: `FEAT-*`
- その他: `WF-*`

`--receipt-id`または`--id-prefix`で明示指定できます。GUI入力自体は`work/requirements/svg-input/`へ置き、ファイル名の`SYS_`、`FEAT_`、`FIX_`で親フローを指定します。

`work/requirements/` に `.md` / `.markdown` / `.txt` の要件定義書が無い場合、受付IDは作らずに受領拒否します。

`work/requirements/` に要件定義書が2件以上ある場合も、どの要件を受け付けるべきか曖昧になるため受領拒否します。標準運用は `1 requirement file = 1 receipt ID` です。

明示的に要件定義書を渡す場合は、以下のように指定できます。

```powershell
python runtime/intake/intake_requirements.py `
  C:\path\to\requirements.md `
  --project-name localty-system-gui `
  --workflow ariadne-new-system-development
```

既定では要件定義書を `work/<採番ID>/design-document/` へ移動します。

元ファイルを残したい場合は `--copy` を付けます。

```powershell
python runtime/intake/intake_requirements.py C:\path\to\requirements.md --copy
```

## Target Work Structure

```text
work/
  <採番ID>/
    design-document/
    process-report/
    test-evidence/
    test-specifications/
    source/
    context/
      agent-context.json
      artifact-index.json
      qa-records.json
      finding-records.json
      decision-records.json
      test-evidence.json
      handoff-package.json
```

## Initial Artifacts

intake 処理では、最低限以下を作成または登録します。

- input requirement document
- `agent-context.json`
- `artifact-index.json`
- `qa-records.json`
- `finding-records.json`
- `decision-records.json`
- `test-evidence.json`
- `handoff-package.json`

## Principle

完成版の要件定義書は `work/requirements/` を投入口にします。

Skill や workflow prompt から作業をオーダーされても、`work/requirements/` に要件定義書が無い場合は harness で受領拒否します。

同じく、`work/requirements/` に複数の要件定義書がある場合も harness で受領拒否します。

投入された要件定義書を会話ログだけに残さず、受付ID単位の作業領域へ移動して追跡可能にします。
