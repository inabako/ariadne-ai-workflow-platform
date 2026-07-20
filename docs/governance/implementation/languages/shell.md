---
language: ja-JP
---

# Shell Rules

この文書は、Ariadne AI Workflow Platform が生成、変更、保守する Unix系 Shell script へ適用する言語固有規範を定義します。

言語別規範は、言語 Tips や好みの実装スタイルを集めるための文書ではありません。各言語で発生しやすい security issue、vulnerability、unsafe side effect、secret leakage、検証不能な実装を防ぐための最低規範です。

対象 Shell は、原則として Bash または明示的に指定された POSIX shell とします。

Shell script は、短く見える一方で、引用、終了 code、path、platform差異、副作用が曖昧になりやすいため、用途を限定して使用します。

## 目的

* 実行 Shell と対応 platform を明示する。
* 引数、path、終了 code を安全に扱う。
* command failure を隠さない。
* destructive operation を制御する。
* configuration と secret を hard-code しない。
* 大規模 logic を Shell へ集約しない。
* Windows script や PowerShell との責務を分離する。

## Shell Selection

### MUST

* shebang で実行 Shell を明示する。
* Bash 固有 syntax を使う場合は Bash を指定する。
* POSIX互換を主張する場合、非互換 syntax を使用しない。
* `/bin/sh` が Bash であると仮定しない。
* required Shell version を README等へ記載する。

例:

```bash
#!/usr/bin/env bash
```

### SHOULD

- 複雑な data処理や長大な business logic には、Python、Go等を検討する。

* Shell は orchestration、environment setup、small automation へ限定する。
* platformごとに script を分ける場合、共通責務を明確にする。

## Strict Mode

Bash では、原則として次を検討します。

```bash
set -Eeuo pipefail
```

### MUST

* strict modeの各挙動を理解して使用する。
* expected non-zero を明示的に扱う。
* pipelineの failure を見逃さない。
* unset variable を意図せず参照しない。
* strict mode を一時解除する場合、範囲と理由を限定する。

strict modeだけで安全性が保証されるとは扱いません。

## Quoting

### MUST

* variable expansion を原則として double quote する。
* command substitutionの結果を無引用で展開しない。
* path や user input を word splitting させない。
* glob展開が必要な箇所と不要な箇所を区別する。
* array を利用可能な Bash では、複数引数を string連結しない。
* `eval` を原則使用しない。

避ける例:

```bash
rm -rf $TARGET_DIR
```

推奨例:

```bash
rm -rf -- "$TARGET_DIR"
```

ただし、削除前の追加 validation を必須とします。

## Arguments

### MUST

* 引数の数と形式を validation する。
* unknown option を明示的に拒否する。
* `--help` を提供する。
* positional argumentの意味を説明する。
* path、URL、identifier を validation する。
* password や token を command line argument として要求しないことを基本とする。
* option parsingの方式を script 内で統一する。

## Variables

### MUST

* global variable と local variable を区別する。
* function 内では `local` を使用可能な Shell で利用する。
* environment variable と internal variable を区別する。
* readonly にできる値は readonly にする。
* magic string や path を散在させない。
* variable 名から用途と scope を判断できるようにする。

### SHOULD

* constant は UPPER_SNAKE_CASE を使用する。
* local variable は lower_snake_case を使用する。
* command result と status code を別々に扱う。
* `IFS` 変更は最小 scope へ限定する。

## Exit Codes

### MUST

* success は0、failure は non-zero とする。
* external commandの exit code を確認する。
* error を出力しただけで0終了しない。
* caller が判断すべき failure code を必要に応じて定義する。
* cleanup failure と primary failureの扱いを決める。
* pipeline や subshell で status が失われないようにする。

## Error Handling

### MUST

* error message を stderr へ出力する。
* failureした operation と対象を示す。
* secret を error へ含めない。
* trap で元の exit code を失わない。
* retry可能な command を限定する。
* error を `|| true` で無条件に無視しない。
* temporary workaround には理由を記載する。

### SHOULD

共通 error function を用意します。

```bash
die() {
 printf 'ERROR: %s\n' "$*" >&2
 exit 1
}
```

## Functions

### MUST

* functionの責務を一つに保つ。
* global state への依存を最小化する。
* argument を明示的に受け取る。
* stdout を data output として利用する場合、log を stderr へ分ける。
* return code と output stringの責務を混同しない。

### SHOULD

* main function を用意する。
  * 実行順序を entrypoint で明確にする。
* function 名は動作を表す。
* reusable function を責務不明の common script へ集めない。

## Paths

### MUST

* current working directory を script directory と仮定しない。
* script自身の location を必要に応じて安全に解決する。
* relative pathの基準を明確にする。
* path traversal を防止する。
* symlink を扱う場合の方針を定義する。
* whitespace、newline、wildcard を含む path を考慮する。
* temporary file には `mktemp`等の安全な仕組みを使用する。

## Destructive Operations

次を destructive operation として扱います。

* `rm`。
* `mv` による上書き。
* repository reset。
* branch 削除。
* data purge。
* volume 削除。
* infrastructure 変更。
* permission 変更。

### MUST

* target が空でないことを確認する。
* root や repository上位 directory を拒否する。
* allowed base path 内であることを確認する。
* `--dry-run` を可能な範囲で提供する。
* Human Check または明示 flag を必要とする。
* operation 前に対象を表示する。
* wildcard 削除を避ける。
* rollback可能性を確認する。

## External Commands

### MUST

* required commandの存在を事前確認する。
* version requirement を必要に応じて確認する。
* command path を無条件に信頼しない。
* user input を command string へ埋め込まない。
* exit code と output を確認する。
* timeout が必要な command を無制限に待機しない。
* network operation を明示する。

## Secret Handling

### MUST

* secret を script へ hard-code しない。
* `set -x`利用時に secret が出力されないようにする。
* environment dump を無制限に行わない。
* secret を command argument へ渡さないことを基本とする。
* temporary file へ secret を保存する場合、permission と cleanup を管理する。
* CI log へ secret を出力しない。

## Portability

### MUST

* target OS と Shell を明示する。
* GNU と BSD commandの option差異を考慮する。
* text encoding を UTF-8とする。
* newline形式を repository方針に合わせる。
* Windows で利用する場合、WSL、MSYS2、Git Bash等の前提を明示する。
* path変換を暗黙に行わない。

## Lint and Formatting

### MUST

* Shell lint tool を利用する。
* format方針を統一する。
* lint抑制には理由を記載する。
* syntax check を CI へ含める。
* generated script を識別可能にする。

## Testing

### MUST

- 主要 function または script flow を test する。

* success と failureの両方を確認する。
* external command を test double へ置換可能にする。
* temporary directory を使用する。
* production環境や real external service へ接続しない。
* destructive operation は dry-run または sandbox で確認する。
* exit code、stdout、stderr を検証する。

## AI Agent 向け規範

AI Agent は Shell script 変更時に次を確認します。

1. target Shell。
2. version。
3. strict mode。
4. quoting。
5. argument validation。
6. path。
7. exit code。
8. destructive operation。
9. secret。
10. external command。
11. portability。
12. lint と test。

## まとめ

* Shell script は用途を限定し、実行 Shell と platform を明示する。
* variable、path、引数を必ず適切に quote する。
* command failure と exit code を隠さない。
* destructive operation には path validation、dry-run、Human Check を設ける。
  * 複雑な business logic を Shell へ集約しない。
