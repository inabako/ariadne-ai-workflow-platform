# Component License Boundaries

この文書は、OSS公開前にlicense boundaryをどのようにreviewするかを記録します。

## ARIADNE Repository Component

次のものはARIADNE repository materialとして扱います。

- runtime helper。
- workflow definition。
- CLIおよびCTL code。
- Context Control、Dispatcher、Review Runtime、RAG、Retrieval、Intake、observability code。
- ARIADNE固有のschema、prompt、template、test、configuration、documentation。

## 外部入力と出力

external repository、user input、generated project file、generated reportは、ARIADNEが処理したという理由だけでARIADNE repository licenseを自動適用されるものではありません。

## Review Rule

componentを配布する場合は、ARIADNE repository codeまたは保護対象material、third-party code、generated content、user-owned contentが含まれるかを確認します。曖昧なcaseは [evidence/legal-review-items.md](evidence/legal-review-items.md) に記録します。
