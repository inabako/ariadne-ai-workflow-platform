---
language: ja-JP
---

# Python Template

この文書は、Python を利用する CLI、API、worker、batch、data processing、agent componentの boilerplate に適用する規範を定義します。

Python template は、実行方法、dependency、type、configuration、test、packaging を明示し、環境差異や暗黙 import による不安定性を減らします。

## 目的

* 再現可能な Python environment を提供する。
* package structure と entrypoint を明確にする。
* type checking、lint、format、test を統合する。
* configuration と secret を安全に扱う。
* scriptの集合ではなく、保守可能な application構造を提供する。
* sync、async、process boundary を明示する。

## Recommended Structure

```text
src/
└── package_name/
    ├── __init__.py
    ├── app/
    ├── domain/
    ├── adapters/
    ├── config/
    └── main.py

tests/
scripts/
docs/
pyproject.toml
README.md
```

### MUST

* application code を package として管理する。
* import path を作業 directory へ依存させない。
* top-level へ無秩序に script を配置しない。
* production package と test helper を分離する。
* module責務を明確にする。
* circular import を作らない。

## Python Version

### MUST

* supported Python version を明示する。
* version range を `pyproject.toml`等へ記載する。
* unsupported version を対象に含めない。
* runtime と CIの version を揃える。
* version 固有 syntax や standard library利用を確認する。

## Dependency Management

### MUST

* dependency を manifest へ記載する。
* application、development、test dependency を区別する。
* reproducibleな version 管理方法を採用する。
* virtual environment を利用する。
* global environment への install を前提にしない。
* package source と license を確認する。
* secret を package index URL へ埋め込まない。

### SHOULD

* `pyproject.toml` を source of truth とする。
* lock file を利用する tool では管理対象に含める。
* optional dependency を feature group として分離する。
* editable installの用途を development に限定する。

## Entry Point

### MUST

* CLI、API、workerなどの entrypoint を明示する。
* import 時に重大な side effect を実行しない。
* `if __name__ == "__main__":`の責務を最小化する。
* package entrypoint と直接 script 実行の差異を管理する。
* exit code を適切に返す。

## Type Hints

### MUST

* public function と主要 domain model へ type hint を付ける。
* `Any` を無制限に利用しない。
* optional value を明示する。
* external data を typed model へ validation する。
* type check failure を無断で無視しない。

### SHOULD

* strictness を段階的に高める。
* Protocol や dataclass を責務に応じて利用する。
* runtime validation と static typing を混同しない。
* cast で問題を隠しすぎない。

## Error Handling

### MUST

* bare `except` を使用しない。
* `Exception`の広範囲 catch を必要以上に行わない。
* exception を黙って握り潰さない。
* custom exception を責務に応じて定義する。
* library code から無断に process終了しない。
* cleanup には context manager を利用する。
* original exception を追跡可能にする。

## Configuration

### MUST

* environment variable を domain logic から直接読まない。
* configuration を typed object へ変換する。
* required value を startup 時に validation する。
* `.env` file を secretの正式保管場所にしない。
* `.env` を commit しない。
* `.env.example` には dummy valueだけを記載する。
* secret を repr、log、error へ出力しない。

## Async

asyncio等を利用する場合:

### MUST

* sync と asyncの boundary を明確にする。
* event loop を nested に起動しない。
* taskの owner と終了条件を明確にする。
* background taskの exception を回収する。
* timeout と cancellation を扱う。
* blocking I/O を event loop上で無制限に実行しない。
* unbounded task 生成を避ける。

## Files and Paths

### MUST

* `pathlib`等を用いて platform差異を考慮する。
* current working directory を暗黙の root として扱わない。
* path traversal を防止する。
* encoding を明示する。
* temporary file には安全な API を使用する。
* Windows と Unixの path、改行差異を必要に応じて test する。

## Logging

### MUST

* `print` を production observabilityの主手段にしない。
* module-level logger を適切に利用する。
* logging configuration を entrypoint 側で行う。
* secret を出力しない。
* exception logの重複を避ける。
* library package が root logger設定を変更しない。

## Formatting and Lint

### MUST

* formatter を一つ定義する。
* lint tool を定義する。
* import sorting方針を統一する。
* CI で実行可能にする。
* generated code を適切に除外する。
* ignore rule に理由を持たせる。

## Testing

### MUST

* test runner を明示する。
* unit test と integration test を区別する。
* filesystem、network、clock、environment を分離する。
* production data や secret を fixture へ含めない。
* test順序へ依存しない。
* temporary directory を安全に利用する。
* warning を無条件に無視しない。
* async testの timeout を設ける。

### SHOULD

* fixture scope を小さく保つ。
* parameterized test を利用する。
* property-based test を parser や boundary へ検討する。
* coverage は重要 behavior を中心に確認する。

## Packaging

### MUST

* package name と import nameの関係を明示する。
* build artifact へ不要な file や secret を含めない。
* license file を含める。
* package metadata を定義する。
* versioning方法を明確にする。
* wheel または distribution artifactの内容を検証する。

## CLI

CLI templateの場合:

### MUST

* help を提供する。
* exit code を定義する。
* stdout と stderr を区別する。
* machine-readable output を必要に応じて提供する。
* destructive operation へ明示 flag または確認を要求する。
* password や token を command argument として要求しないことを基本とする。

## Generated Structure

template は必要に応じて次を含めます。

```text
src/
tests/
scripts/
docs/
pyproject.toml
README.md
.env.example
.gitignore
Dockerfile
```

## AI Agent 向け規範

AI Agent は Python template 変更時に次を確認します。

1. Python version。
2. package structure。
3. entrypoint。
4. dependency。
5. type。
6. exception。
7. configuration。
8. async boundary。
9. path。
10. lint。
11. test。
12. packaging。

## まとめ

* Python template は package、environment、entrypoint を明確にする。
* global environment や current directory へ依存しない。
* type、validation、exception を明示する。
* sync と async、script と application を混同しない。
* test、lint、format、packaging を初期構成へ含める。
