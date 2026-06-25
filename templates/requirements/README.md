# Requirements Templates

このディレクトリは、ロボティクス向け要件定義書のひな形を格納します。

## Templates

| Directory | Purpose |
| --- | --- |
| `new-system/` | 新しいrobotics systemを立ち上げる要件定義書 |
| `feature-maintenance/` | 新機能追加および保守開発の要件定義書 |

## Repository Control

新機能および保守開発では、要件定義書内に target repository を必ず記載します。

これにより、`.env` に固定repositoryを登録しなくても、案件ごとに対象repository / target branch を変えられます。

`runtime/scm/prepare_repository.py` は、CLI引数がない場合、要件定義書内の `Repository Control` を読み取ります。

`runtime/intake/intake_requirements.py` は、repository が読み取れない要件定義書を受領しません。

## Intake Location

完成版の要件定義書は `work/requirements/` に配置します。

未完成の箇条書き草案は `work/requirements/draft/` に配置します。`/requirement-discovery` workflow はこの草案を精査し、必要な質問と人間レビューを経てから完成版を `work/requirements/` に保存します。

`/requirement-discovery` は review draft 作成前に Noise Reduction Phase を実行し、未知語、用語衝突、別名、文書矛盾、曖昧表現、AI誤認ポイント、業務ルール欠落を確認します。`BLOCK` の場合は Human Interview Sheet を返し、完成版要件定義書を作成しません。

新システム立ち上げ、新機能追加、保守開発のいずれでも、この投入口を共通で使います。

`work/requirements/` に要件定義書が無い場合、Skill や workflow prompt から作業をオーダーされても intake harness は受領拒否します。

`work/requirements/` に要件定義書が2件以上ある場合も受領拒否します。標準運用は `1 requirement file = 1 receipt ID` です。
