# Requirements Intake Inbox

Completed requirement documents go in this directory.

Unfinished bullet-list drafts go in:

```text
work/requirements/draft/
```

GUI SVG inputs go in:

```text
work/requirements/svg-input/
```

Use `SYS_<name>.svg`, `FEAT_<name>.svg`, or `FIX_<name>.svg` so the parent workflow can claim the correct GUI input after creating its Issue work area.

Use `/requirement-discovery` to inspect a draft, ask clarification questions, create a review draft, and save the final requirement document here only after human OK.

このディレクトリは、完成版の要件定義書を配置する intake inbox です。

新システム立ち上げ、新機能追加、保守開発のいずれでも、workflow を開始する前に完成版の要件定義書をここへ置きます。

`runtime/intake/intake_requirements.py` は、引数で要件定義書が渡されない場合、このディレクトリから `.md` / `.markdown` / `.txt` を読み取ります。

このディレクトリに要件定義書が無い場合、Skill や workflow prompt から作業をオーダーされても harness は受領拒否します。

このディレクトリに要件定義書が2件以上ある場合も、どちらを受け付けるべきか曖昧になるため harness は受領拒否します。

標準運用は `1 requirement file = 1 receipt ID` です。

要件定義書には `Repository Control` を必ず記載してください。repository が読み取れない要件定義書は受領されません。
