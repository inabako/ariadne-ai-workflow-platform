# Test Logs

`logs/test/` は、ローカルテストで確認しやすくするための生成ログ置き場です。

主な出力:

- `runtime-trace-cli-integration/sequence/runtime-events.log`: active trace 内で複数 CLI process を実行したとき、同じ trace id で sequence が workflow 全体の通番になることを確認するログ。
- `runtime-trace-cli-integration/without-active/runtime-events.log`: active trace なしで複数 CLI process を実行したとき、command ごとに trace id と sequence が分かれることを確認するログ。

この README 以外の生成ログは Git 管理しません。
