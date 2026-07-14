# Network Module

VPC、LAN、subnet、routing、listen address、VPN / Relay 拡張の責務を持つ module です。

この template では provider-neutral な契約だけを出力します。
コピー後に target infrastructure が決まったら、VPS、home server、k3s、ECS、cloud network provider へ写像します。

固定IPは共通moduleに埋め込まず、共有成果物と environment 変数から決めます。
