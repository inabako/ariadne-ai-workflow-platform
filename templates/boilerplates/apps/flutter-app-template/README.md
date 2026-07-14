# Flutter Boilerplates

Flutter multi-platform workflowが、対象platformと既存構成を確認したうえでwork配下へコピーする初期構造です。

このtemplateは完成アプリケーションではありません。目的は、共通コード、platform interface、test、integration test、evidenceの置き場を最初から迷わないようにすることです。

## 種別

- `application`: platform未確定または最小構成
- `mobile`: Android / iOS中心
- `web`: Flutter Web中心
- `desktop`: Windows / macOS / Linux中心
- `multi-platform`: mobile / web / desktopをまたぐ構成

署名、Store配布、本番credential、実機試験はHuman Check後に親workflowで扱います。
