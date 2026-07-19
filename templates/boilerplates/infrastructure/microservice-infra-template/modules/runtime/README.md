# Runtime Module

Docker、systemd、k3s、ECS の runtime contract を扱う module です。

優先順:

1. Docker
2. systemd
3. k3s
4. ECS

この module は application source code を生成しません。
port mapping、volume mount、restart policy、health check、environment injection の基盤側契約だけを持ちます。
