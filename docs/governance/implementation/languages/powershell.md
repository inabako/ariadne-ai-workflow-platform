---
language: ja-JP
---

# PowerShell Rules

この文書は、Ariadne AI Workflow Platform が生成、変更、保守する PowerShell scriptおよび module へ適用する言語固有規範を定義します。

言語別規範は、言語 Tips や好みの実装スタイルを集めるための文書ではありません。各言語で発生しやすい security issue、vulnerability、unsafe side effect、secret leakage、検証不能な実装を防ぐための最低規範です。

対象には次を含みます。

* Windows automation。
* development environment setup。
* repository maintenance。
* build、test、deployment helper。
* administration script。
* cross-platform PowerShell automation。
* PowerShell module。

## 目的

* PowerShell version と target OS を明示する。
* object pipeline を文字列処理へ退化させない。
* parameter、error、exit code を明確にする。
* destructive operation へ WhatIf、Confirm、Human Check を適用する。
* Windows path、encoding、execution policy差異を扱う。
* secret を history、transcript、log へ露出しない。
* script を責務別に階層化する。

## Supported Version

### MUST

* Windows PowerShell 5.1または PowerShell 7+のどちらを対象とするか明示する。
* cross-platform を主張する場合、Windows 固有 cmdlet や path を分離する。
* required module と version を記載する。
* CI と実行 environmentの version を揃える。
* `$PSVersionTable`依存分岐を無秩序に増やさない。

### SHOULD

* 新規 cross-platform automation では PowerShell 7+を検討する。
* Windows PowerShell 5.1対応が必要な場合、互換性 test を行う。
* version 固有機能には fallback または明示的 failure を用意する。

## Script Structure

推奨構成:

```text
scripts/
├── common/
├── windows/
├── development/
├── test/
├── build/
└── maintenance/
```

moduleの場合:

```text
ModuleName/
├── ModuleName.psd1
├── ModuleName.psm1
├── Public/
├── Private/
└── Tests/
```

### MUST

* scriptの目的と target environment を明示する。
* public function と private function を分離する。
* root直下へ無秩序に script を配置しない。
* script 名から operation を判断できるようにする。
* common module へ特定 workflow 固有処理を集めない。
* entrypoint と helper を分離する。

## Naming

### MUST

* function は Approved Verb を使用した `Verb-Noun`形式を基本とする。
* parameter は PascalCase を使用する。
* local variable は意味の分かる名称にする。
* boolean parameter には switch parameter を適切に利用する。
* alias を production script 内で使用しない。
  * 省略形 cmdlet 名を使用しない。
* built-in automatic variable と衝突する名称を避ける。

例:

```powershell
Get-AriadneContext
Test-RuntimePrerequisite
Invoke-WorkflowValidation
Remove-WorkArtifact
```

## Parameters

### MUST

* reusable script では `param()` を使用する。
* type を明示できる parameter には type を指定する。
* mandatory parameter を明示する。
* ValidateSet、ValidatePattern、ValidateRange等を必要に応じて利用する。
* path parameter を validation する。
* password や token を plain string parameter として要求しないことを基本とする。
* default値を安全側にする。

### SHOULD

* advanced function には `[CmdletBinding()]` を使用する。
* pipeline input を受ける場合、behavior を明確にする。
* parameter set で operationの曖昧さを減らす。
* help message を用意する。

## CmdletBinding and ShouldProcess

destructive または state-changing operation では、次を基本とします。

```powershell
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(...)
```

### MUST

- 削除、上書き、公開、権限変更では `ShouldProcess` を利用可能にする。

* `-WhatIf` で対象 operation を確認できるようにする。
* `-Confirm:$false` を script 内部で無断使用しない。
* Human Check 対象 operation を PowerShell confirmationだけで代替しない。
* ShouldProcessの target と action を具体的にする。

## Error Handling

### MUST

* terminating error と non-terminating error を理解して扱う。
  * 必要な operation では `-ErrorAction Stop` を使用する。
* `$ErrorActionPreference` 変更は scope を明確にする。
* error を握り潰さない。
* `try`、`catch`、`finally` を resource lifecycle に応じて利用する。
* `throw` する error へ operation と対象を含める。
* secret を error record へ含めない。
* `$LASTEXITCODE` を native command 実行後に確認する。

### MUST NOT

* `SilentlyContinue` で重大な failure を隠さない。
* empty catch block を作らない。
* Write-Error 後に success exit する状態を放置しない。
* `$?`だけで native commandの詳細な failure を判断しない。

## Output Streams

PowerShellの stream を用途に応じて使い分けます。

* Success output。
* Error。
* Warning。
* Verbose。
* Debug。
* Information。
* Progress。

### MUST

* reusable function は object を success output へ返す。
* human-readable message を data object と混在させない。
* log目的の message を `Write-Output` へ流しすぎない。
* error は error stream へ出力する。
* secret を Verbose や Debug へ出力しない。
* progress表示を machine-readable output と混在させない。

### SHOULD

* status message は Verbose または Information を利用する。
* caller が加工可能な custom object を返す。
* formatting は display layer へ分離する。
* `Format-Table`等を function 内部の return contract にしない。

## Object Pipeline

### MUST

* object を早期に文字列化しない。
* `Select-Object`、`Where-Object`等を責務に応じて利用する。
* property存在を確認する。
* pipeline input が大量の場合、performance を考慮する。
* external command output を structured object と誤認しない。

### SHOULD

* `ForEach-Object`の濫用より通常 loop が明確な場合はそちらを使う。
* custom object へ meaningful property 名を付ける。
* output type を documentation へ記載する。

## Native Commands

### MUST

* executableの存在を確認する。
* argument を文字列連結しすぎない。
* path と argument を区別する。
* `$LASTEXITCODE` を確認する。
* stdout と stderrの扱いを明確にする。
* timeout または process終了条件を必要に応じて設ける。
* command injection を防止する。
* platformごとの quoting差異を考慮する。

### SHOULD

* `Start-Process` と直接呼出しを用途で使い分ける。
* argument list を明示する。
* output capture が必要な場合、encoding を確認する。
* native command wrapper を責務ごとに用意する。

## Paths

### MUST

* `Join-Path`等を利用する。
* path separator を hard-code しない。
* relative pathの基準を明確にする。
* `Resolve-Path` 結果を利用する前に存在を確認する。
* path traversal を防止する。
* empty path や root path を destructive operation で拒否する。
* symlink、junction、reparse point を risk に応じて確認する。
* long path と space を含む path を考慮する。

## Encoding

### MUST

* text fileの encoding を明示する。
* 原則として UTF-8を使用する。
* PowerShell versionごとの default encoding差異を考慮する。
* JSON、YAML、Markdown、source file を書き込む際に encoding を指定する。
* BOM有無を repository方針に合わせる。
* native command outputの encoding差異を確認する。

### SHOULD

* file write用 helper で encoding方針を統一する。
* Windows PowerShell 5.1と PowerShell 7の差異を test する。
  * 改行コードを repository方針に合わせる。

## Secret Handling

### MUST

* secret を script へ hard-code しない。
* plain text credential を parameter や log へ出力しない。
* SecureStringだけで完全に安全と仮定しない。
* credential objectの scope と lifecycle を管理する。
* transcript へ secret が記録される可能性を考慮する。
* command history へ secret を残さない。
* environment variable一覧を無制限に出力しない。
* secret fileの permission を確認する。

## Configuration

### MUST

* environment 固有 path や URL を hard-code しない。
* configuration file または parameter から取得する。
* required configuration を開始前に validation する。
* secret と通常 configuration を分離する。
* effective configuration を出力する場合、secret を mask する。
* machine 固有値を共通 script へ埋め込まない。

## Destructive Operations

### MUST

* target path、resource、repository を再確認する。
* empty value を拒否する。
* allowed scope 内であることを確認する。
* `SupportsShouldProcess` を利用する。
* `-WhatIf` 対応を提供する。
* Human Check 対象 operation は承認前に実行しない。
* recursive deletionの対象を表示する。
* rollback または backup を必要に応じて用意する。
* wildcard expansion を安全に扱う。

## Modules

### MUST

* module manifest を用意する。
* exported function を限定する。
* private helper を export しない。
* module version を管理する。
* required module と compatible PowerShell version を記載する。
* import 時に重大な副作用を起こさない。
* nested module や script moduleの責務を明確にする。

## Comment-Based Help

### SHOULD

public function や entrypoint には次を記載します。

* Synopsis。
* Description。
* Parameter。
* Example。
* Output。
* Notes。
* Link。

help 内容と実装を一致させます。

## Lint and Formatting

### MUST

* PowerShell用 static analysis を利用する。
* repository 内で format方針を統一する。
* rule抑制には理由を記載する。
* CI で syntax と analysis を実行する。
* generated script を識別可能にする。
* alias使用や unsafe command を検出する。

## Testing

### MUST

* unit または script test framework を定義する。
* success と failure を確認する。
* native command を mock または sandbox 化する。
* filesystem操作には temporary directory を使用する。
* destructive operation を WhatIf または isolated environment で test する。
* Windows PowerShell と PowerShell 7の対象 version を必要に応じて検証する。
* exit code、output object、error stream を確認する。
* test 後に environment を cleanup する。

## Cross-Platform

### MUST

cross-platform 対応を主張する場合、次を確認します。

* path。
* line ending。
* encoding。
* available cmdlet。
* native executable。
* permission model。
* filesystem case sensitivity。
* environment variable。
* service 管理。
* process signal。

Windows 固有処理は専用 function または directory へ分離します。

## AI Agent 向け規範

AI Agent は PowerShell 変更時に次を確認します。

1. PowerShell version。
2. target OS。
3. function naming。
4. parameter validation。
5. ShouldProcess。
6. error action。
7. native command exit code。
8. output stream。
9. path。
10. encoding。
11. secret。
12. lint と test。

## まとめ

* PowerShell成果物は version、target OS、output contract を明示する。
* object pipeline を維持し、data と human-readable message を分離する。
* native commandの exit code と encoding を確認する。
* destructive operation には ShouldProcess、WhatIf、Human Check を適用する。
* Windows 固有処理と cross-platform処理を分離する。
