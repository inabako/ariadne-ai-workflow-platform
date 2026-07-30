---
language: ja-JP
---

# Python Rules

この文書は、Ariadne AI Workflow Platform が生成、変更、保守する Python成果物へ適用する言語固有規範を定義します。

言語別規範は、言語 Tips や好みの実装スタイルを集めるための文書ではありません。各言語で発生しやすい security issue、vulnerability、unsafe side effect、secret leakage、検証不能な実装を防ぐための最低規範です。

対象には次を含みます。

* CLI。
* API。
* worker。
* batch。
* data processing。
* AI Agent。
* automation script。
* library。
* test tool。

共通の security、testing、configuration、Evidence、Human Check については、上位の Implementation Governance を参照します。

## 目的

* Python version と実行 environment を再現可能にする。
* scriptの集合ではなく、責務を持つ package として管理する。
* type、exception、dependency、async boundary を明示する。
* current working directory や global state への暗黙依存を減らす。
* formatter、lint、test、package build を標準化する。
* Windows、Linux、container間の差異を扱う。

## Supported Version

### MUST

* supported Python version を明示する。
* `pyproject.toml`などへ version range を記載する。
* CI と runtime で同じ major/minor version を使用する。
* support終了済み version を新規採用しない。
* version依存 syntax や standard library利用を確認する。

### SHOULD

* 原則として現在保守対象の stable version を採用する。
  * 複数 version を support する場合、CI matrix で検証する。
* version 更新は dependency compatibility とあわせて行う。

## Project Structure

推奨構成:

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
* import path を current directory へ依存させない。
* production code と test utility を分離する。
* top-level へ無秩序に `.py` file を配置しない。
* circular import を作らない。
* package 名と distribution 名の関係を明示する。

### SHOULD

* `src` layout を採用する。
* feature または責務単位で module を分ける。
* `utils.py` や `common.py` を責務不明の集積所にしない。
* private module を必要に応じて underscore で識別する。

## Entry Point

### MUST

* CLI、API、workerなどの entrypoint を明示する。
* import 時に network接続、file 生成、process起動などの重大な副作用を実行しない。
* `if __name__ == "__main__":`の責務を最小化する。
* library module から `sys.exit()` を実行しない。
* exit codeの意味を定義する。

### SHOULD

* console script entrypoint を package metadata で定義する。
* dependency construction を entrypoint へ寄せる。
* application logic を entrypoint から分離する。

## Naming

### MUST

* package、module、function、variable は原則 snake_case を使用する。
* class は PascalCase を使用する。
* constant は UPPER_SNAKE_CASE を使用する。
* privateな識別子には必要に応じて leading underscore を使用する。
* built-in 名を変数名で上書きしない。
* `data`、`info`、`obj`など曖昧な名称を広い scope で使用しない。

### SHOULD

* boolean は `is_`、`has_`、`can_`、`should_`など意味が分かる形にする。
* unit を名称へ含める。
* exception class は `Error` で終える。
* protocol や interface相当の責務が分かる名前を使用する。

## Type Hints

### MUST

* public function、主要 domain model、boundary へ type hint を付ける。
* optional value を明示する。
* `Any` を無制限に利用しない。
* external input を typed model へ変換する。
* type checkerの error を理由なく無視しない。
* `# type: ignore` には対象 code または理由を付ける。

### SHOULD

* modernな built-in generic表記を採用する。
* `Protocol` を利用側 contract に必要な場合だけ使用する。
* immutable value には frozen dataclass等を検討する。
* `TypedDict`、dataclass、validation model を用途に応じて使い分ける。
* cast で設計上の不整合を隠さない。

## Error Handling

### MUST

* bare `except:` を使用しない。
* 広範囲な `except Exception` を通常処理へ多用しない。
* exception を黙って握り潰さない。
* original exception を追跡可能にする。
* expected failure と programming error を区別する。
* cleanup には context manager を利用する。
* secret を exception message へ含めない。

### SHOULD

* domain または application 固有 exception を定義する。
* exception hierarchy を深くしすぎない。
* boundary で external exception を内部 contract へ変換する。
* retry可能な exception を識別可能にする。
* `raise ... from ...` を適切に使用する。

## Context Manager

### MUST

次を扱う処理では context manager を優先します。

* file。
* transaction。
* lock。
* temporary resource。
* network connection。
* session。
* resource lifecycle。

resource を取得したまま release しない構造を作りません。

## Dependency Management

### MUST

* dependency を `pyproject.toml`等の manifest へ記載する。
* application、development、test dependency を区別する。
* global Python environment への install を前提にしない。
* virtual environment を使用する。
* dependency version を再現可能に管理する。
* package取得元と license を確認する。
* private package credential を URL へ埋め込まない。

### SHOULD

* `pyproject.toml` を primary configuration とする。
* lock file を利用する tool では version control対象とする。
* optional feature を dependency group へ分離する。
  * 不要な transitive dependency を増やさない。
* dependency 追加前に standard library で代替可能か確認する。

## Configuration

### MUST

* environment variable を domain logic から直接読まない。
* configuration を typed object へ変換する。
* application起動時に validation する。
* `.env` を production secret保管場所にしない。
* `.env` を commit しない。
* `.env.example` には dummy valueだけを記載する。
* secret field を `repr` や log へ表示しない。

## File and Encoding

### MUST

* text fileの encoding を明示する。
* 原則として UTF-8を使用する。
* `pathlib`等を利用して platform差異を扱う。
* current working directory を repository root と仮定しない。
* file path は application root または configuration から解決する。
* path traversal を防止する。
* temporary file には安全な API を使用する。

### SHOULD

* newline差異を test する。
* Windows 固有 path と Unix path を必要に応じて検証する。
* binary と text mode を明確に分ける。
* file read/write size を無制限にしない。

## Async

asyncio等を利用する場合:

### MUST

* sync と asyncの境界を明確にする。
* event loop を nested に起動しない。
* taskの owner と終了条件を明示する。
* background taskの exception を回収する。
* timeout と cancellation を扱う。
* blocking I/O を event loop上で直接長時間実行しない。
* unbounded task 生成を行わない。

### SHOULD

* structured concurrency を意識する。
* task group を利用可能な version では検討する。
* semaphore等で concurrency を制限する。
* async を使うこと自体を目的にしない。

## Concurrency and Process

### MUST

* thread、process、asyncの選択理由を明確にする。
* shared mutable state を同期なしに共有しない。
* process間で利用できない object を暗黙に共有しない。
* child processの exit status を確認する。
* subprocess には timeout を設定する。
* command引数を shell string へ直接連結しない。

### SHOULD

* shell=False を基本とする。
* CPU-bound処理と I/O-bound処理を区別する。
* worker数を resource に応じて制限する。
* process終了時の cleanup を定義する。

## Logging

### MUST

* production observability を `print()`だけに依存させない。
* logging configuration を entrypoint または application bootstrap で行う。
* library module が root logger設定を変更しない。
* secret、credential、personal data を出力しない。
* exception を複数 layer で重複記録しすぎない。
* structured logging が必要な場合は key を統一する。

## Formatter and Lint

### MUST

* formatter を一つ定義する。
* lint tool を定義する。
* import sorting を統一する。
* type checker を定義する。
* CI で同じ command を実行する。
* ignore rule に理由を持たせる。
* generated codeの除外範囲を明示する。

推奨される役割:

```text
Formatter
Lint
Import Check
Type Check
Test
Security Check
```

tool自体は project要件に応じて選択します。

## Testing

### MUST

* test runner を一つ定義する。
* unit、integration、end-to-end を区別する。
* test順序へ依存しない。
* filesystem、environment、clock、network を制御する。
* production data と secret を fixture へ含めない。
* temporary directory を利用する。
* async test へ timeout を設ける。
* warning を無条件に無視しない。

### SHOULD

* parameterized test を利用する。
* fixture scope を小さくする。
* parser や validation へ property-based test を検討する。
* coverage は重要 behavior を中心に評価する。
* representative environment で package install test を行う。

## Packaging

### MUST

* package metadata を定義する。
* versioning方法を明確にする。
* build artifact へ secret や不要 file を含めない。
* wheel または source distributionの内容を確認する。
* license情報を含める。
* package build を CI または test で検証する。

## Security

### MUST

* `eval`、`exec`、unsafe deserialization を不用意に使用しない。
* `pickle`等の信頼できない data を読み込まない。
* shell command へ外部入力を直接渡さない。
* temporary file 名を手動生成しない。
* YAML等の loader は safeな方式を使用する。
* web framework利用時は input validation と authorization を server 側で行う。
* dependency security alert を確認する。

## AI Agent 向け規範

AI Agent は Python code 変更時に次を確認します。

1. supported version。
2. package boundary。
3. entrypoint。
4. type。
5. exception。
6. resource lifecycle。
7. async または process boundary。
8. configuration。
9. encoding と path。
10. dependency。
11. formatter、lint、type check。
12. test と package build。

## まとめ

* Python成果物は package、version、environment を明示する。
* import 時の副作用と current directory依存を避ける。
* type、exception、resource lifecycle を明確にする。
* sync、async、thread、process を目的に応じて使い分ける。
* formatter、lint、type check、test、package build を再現可能にする。
