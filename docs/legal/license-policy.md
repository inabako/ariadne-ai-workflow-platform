# ライセンスポリシー

この文書は、repositoryのlicense boundaryと、OSS公開に向けたlicense policyを記録します。

## 現在のRepository License

ARIADNEのrepository licenseは `AGPL-3.0-or-later` です。

```text
GNU Affero General Public License v3.0 or later
SPDX-License-Identifier: AGPL-3.0-or-later
```

`LICENSE` にはGNU Affero General Public License Version 3の正式本文を配置します。`or later` の選択は、SPDX identifier、package metadata、README、公開文書で示します。

## `or-later` の意味

`AGPL-3.0-or-later` は、利用者がGNU Affero General Public License Version 3、またはFree Software Foundationが将来公開する後継versionのいずれかを選択できることを意味します。

これは `AGPL-3.0-only` ではありません。

## 生成Artifact

ARIADNEは、code、document、design artifact、configuration、image、diagram、report、その他の出力を生成するtoolとして使うことを想定しています。ARIADNEをtoolとして使用したという理由だけで、生成出力へARIADNE repository licenseを自動適用する方針ではありません。

生成artifactのlicenseは、適用法令、入力dataの権利、third-party license、利用したAI modelまたはexternal serviceの規約に従って、利用者が責任を持って判断します。

## ARIADNE素材を含む場合

生成artifactにARIADNEのsource code、保護対象template、その他repository materialが含まれる場合、そのcopyまたは結合materialには別途license上の義務が生じる可能性があります。

この文書は法的助言ではありません。release前に、公開license policyと第三者license reviewを適切なreviewerと確認してください。
