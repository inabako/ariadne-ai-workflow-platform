# Workflow Skills

このディレクトリは、Localty robotics workflow を開始するための Skill entrypoint を格納します。

## Skills

| Slash Command | Skill | Delegated Prompt | Purpose |
| --- | --- | --- | --- |
| `/robotics-new-system` | `robotics-new-system/` | `/new-robotics-system-development` | 新しい robotics system を立ち上げる |
| `/robotics-feature-maintenance` | `robotics-feature-maintenance/` | `/robotics-maintenance-development` | 既存 robotics system の新機能追加または保守開発を行う |

## Intake Rule

どちらの Skill も、開発本体に入る前に `runtime/intake/intake_requirements.py` と `/pre-development-preparation` を通します。

`work/requirements/` に完成版の要件定義書が1件だけある状態が必要です。

以下の場合は harness で受領拒否します。

- 要件定義書が無い
- 要件定義書が2件以上ある
- 要件定義書から `Repository Control` が読み取れない

会話ログだけを根拠に intake 済みとして扱ってはいけません。
