# Templates

このディレクトリは、Ariadne workflow が再利用するテンプレートをジャンル別に置きます。

| Directory | Purpose |
| --- | --- |
| `artifacts/` | workflow 実行で作成する文書成果物のひな形。requirements、design、process report、shared artifacts、test evidence、test specifications を含みます。 |
| `workflows/` | 特定 workflow や sub-workflow 専用のひな形。IaC、Noise Reduction、Self Improvement、GUI/Web SVG layout を含みます。 |
| `repository/` | target repository に配置する設定ファイルのひな形。 |
| `boilerplates/` | application、service、infrastructure、MCP など、コピーして土台にする実装 boilerplate。 |

`boilerplates/` は実装土台として独立管理し、それ以外は用途の近いジャンル配下にまとめます。
