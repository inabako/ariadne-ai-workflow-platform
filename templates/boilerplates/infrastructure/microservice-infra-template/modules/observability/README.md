# Observability Module

logs、metrics、health、restart count、alert hook、dashboard 拡張の責務を持つ module です。

最低限見る signal:

- service / container status
- connection count
- error count
- restart count
- last communication time

alert webhook は real secret ではなく、外部 secret source への参照として扱います。
