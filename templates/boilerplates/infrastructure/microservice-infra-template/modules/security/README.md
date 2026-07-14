# Security Module

firewall、security group、TCP / UDP allow rule、SSH制限、health / metrics exposure を扱います。

方針:

- default deny
- public exposure 最小
- admin access は CIDR 制限
- internal service は不必要に公開しない
- secret は扱わない
