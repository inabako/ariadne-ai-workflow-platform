# Runtime Common

`runtime/common/` は、runtime 間で共有する utility を格納します。

## Files

| File | Purpose |
| --- | --- |
| `common.py` | path、JSON、artifact index、timestamp などの共通処理 |
| `env.py` | `.env` 読み込み、CSV形式env値、GitHub repository解決 |
| `requirements.py` | 要件定義書から Repository Control を読み取る処理 |

## Environment Policy

GitHub / SCM 連携で必要な値は、repository root の `.env` から読み込みます。

- `.env.example`: 共有可能なキー一覧
- `.env`: ローカル実値、commit禁止
- `.gitignore`: `.env` と `.env.*` を除外し、`.env.example` は追跡対象

実値やtokenを prompt、schema、source code に直接書かないでください。

案件ごとに変わる repository は、要件定義書の `Repository Control` に必ず記載します。

repository が読み取れない要件定義書は intake で受領しません。
