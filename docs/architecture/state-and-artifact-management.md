# StateとArtifact管理

ARIADNEは、workflow出力を会話記憶ではなくartifactとして扱います。

## State

State fileは、現在のworkflow進捗、選択されたoption、resume hint、blocking conditionを記録します。後続runtime commandやhuman reviewerが検査できるよう、十分に構造化します。

## Artifacts

Artifactには、要件、設計note、review、evidence、report、生成template、release manifest、validation outputが含まれます。Git管理するartifactは文書化されたrepository locationに置きます。local生成された作業dataは、workflowが明示的に昇格しない限り、ignore対象workspaceへ置きます。

## Evidence

Evidenceは、何を確認したか、いつ確認したか、どのcommandまたはreviewが生成したか、どの結果が観測されたかを特定できる必要があります。

## 保持方針

公開release artifactには、secret、顧客情報、private URL、local user path、未公開project detailを含めてはいけません。
