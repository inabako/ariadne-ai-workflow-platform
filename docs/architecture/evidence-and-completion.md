# Evidenceと完了条件

ARIADNEの完了判定は、command exitの成功だけではなく、review可能なevidenceに基づきます。

## Evidence種別

- unit、integration、UI、runtime、acceptance checkによるtest evidence。
- human review、Review Council output、specialist agent reportによるreview evidence。
- 構造化されたcommand outputによるruntime evidence。
- validation script、manifest、checksum、release noteによるrelease evidence。

## 完了条件

workflowは実行前にcompletion criteriaを定義します。taskは、関連artifactが存在し、必要なcheckが通過または明示的に受容され、必要なHuman Gate判断が記録されたときにのみ完了です。

## Releaseでの利用

release candidateには、release checklist、validation result、release manifest、known limitationsを含めます。失敗したcheckは、human reviewerが解決するまで見える状態に残します。
