# Output Language Policy

## 目的

このrepositoryで生成・保存する人間向けのreport、document、review、evidence、RAG source Markdownは、原則として日本語で記述します。

この規約は、Agent、Skill、runtime helper、templateから生成される成果物の既定言語を安定させるための共通ルールです。

## 既定言語

- 既定の出力言語は日本語です。
- user が明示的に別言語を指定した場合のみ、その指定言語を優先します。
- 既存artifactを追記・修正する場合も、周辺文脈に反しない限り日本語へ寄せます。

## 英語を許容するもの

次の要素は英語のまま残してかまいません。

- source code、identifier、package名、module名、class名、function名
- command、option、environment variable、file path、URL
- Git / GitHub / VSCode / Docker / Python / Go などの固有名詞
- API名、protocol名、log level、status値、JSON key、schema field
- repositoryや外部toolの正式名称
- 引用元が英語の場合の短い引用。ただし要約は日本語で補足します。

## 成果物ルール

- Markdownの見出し、説明文、要約、判断理由、Human Review、Next Actionは日本語で書きます。
- front matterには `language: ja-JP` を入れます。既存schemaに無い場合でもMarkdown sourceでは追加してかまいません。
- RAG source Markdownは、検索性のために専門用語を残しつつ、本文の主説明を日本語にします。
- GitHub Issue / PR / comment / merge comment の本文は、target repositoryが日本語運用の場合は日本語にします。
- 英語templateや英語reportを参照した場合は、貼り付けずに日本語へ要約・再構成します。

## 検証

生成後は、可能な範囲で次の検証を行います。

```powershell
uv run --project runtime python runtime/workflow/validate_output_language.py `
  --paths work rag docs `
  --fail-on-violation
```

この検証は「英語語句が含まれるか」ではなく、「人間向け本文が英語主体になっていないか」を確認します。
