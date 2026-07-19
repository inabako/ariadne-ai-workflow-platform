# SDKプログラム入力ディレクトリ

このディレクトリは、`/requirement-discovery` のSDK事前解析で使うSDKプログラム一式を置く場所です。

```text
work/requirements/sdk/
```

SDKプログラムがここに存在する場合、要件定義工程で次のコマンドにより事前解析できます。

```powershell
aiwfctl sdk analyze --work-id <work-id>
aiwfctl sdk discover --work-id <work-id>
```

## 置くもの

- SDKプログラム本体
- SDKのsource code
- package定義
- dependency定義
- SDKに同梱されているREADME
- SDKに同梱されているsample code
- SDKに同梱されているconfig example
- SDKに同梱されているAPI reference / OpenAPI / Swagger
- SDKに同梱されているauth / credential管理説明
- SDKに同梱されているLICENSE
- SDKに同梱されているCHANGELOG
- SDKに同梱されているtest / mock / sandbox関連ファイル

## 置かないもの

- API key
- access token
- password
- private key
- production secret
- 個人端末固有のcredential
- SDKプログラムから生成された巨大なbuild成果物
- `node_modules`、`.venv`、`dist`、`build` などの生成物
- SDKプログラムと無関係な調査メモ
- SDKプログラムと無関係な外部記事全文

secret-like literalが検出された場合、SDK事前解析は値そのものをコピーせず、Human Checkが必要な検出事実だけを記録します。

## 解析後の主な出力

SDK事前解析の出力は、作業IDごとに次へ保存されます。

```text
work/<work-id>/reports/sdk-analysis-report.md
work/<work-id>/context/sdk-analysis-context.json
work/<work-id>/context/sdk-files.json
work/<work-id>/requirements/sdk-integration-requirements.md
work/<work-id>/reports/sdk-external-discovery-report.md
work/<work-id>/context/sdk-external-discovery.json
work/<work-id>/requirements/sdk-external-requirements.md
```

`sdk-analysis-context.json` は Context First manifest に `sdk-analysis` として登録されます。

`sdk-files.json` には、解析対象ファイルのrelative path、file size、SHA-256、検出言語、package manager、cloud provider候補を記録します。

AWS / GCP SDKの場合は、cloud provider、言語、package manager、SDK世代、候補サービス、credential model、region / project要件、local test候補、cloud固有のHuman Checkも整理します。

Stripe SDKの場合は、payment vendor、言語、package manager、候補payment service、API key / webhook signing secret、test mode、idempotency、PCI境界、返金・chargeback・税・通貨などのHuman Checkも整理します。

`sdk-external-discovery.json` は Context First manifest に `sdk-external-discovery` として登録されます。これはSDKプログラムから抽出したpackage名、version、repository URL、README内URLなどをもとに、公式docs、package registry、release notes、security advisory、deprecated / unsupported確認へつなぐ検索計画です。

外部ページ本文を丸ごと保存せず、確認結果を残す場合はclaim、根拠URL、version、制約、Human Checkだけをcompactに残します。

## 要件定義への反映方針

完成版の要件定義書には、SDKプログラムの全文やsource code全文ではなく、後続workflowが迷わないために必要な内容だけを反映します。

- SDKプログラム格納場所
- 参照した解析結果
- 外部関連資料discovery結果
- SDK名、version、package情報
- AWS / GCP provider、候補サービス、region / project要件
- Stripe payment vendor、候補payment service、webhook / idempotency / test mode要件
- 認証方式とcredential管理要件
- timeout / retry / rate limitなどの制約
- license、vendor lock-in、cost、production利用可否
- test double / mock / sandbox可否
- Human Checkが必要な未確定事項

SDK採用可否、license、vendor lock-in、credential管理、production network利用、cost、deprecated / unsupported SDK、security不明点は、人間確認なしに確定しません。
