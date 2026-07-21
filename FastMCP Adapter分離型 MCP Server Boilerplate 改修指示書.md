# FastMCP Adapter分離型 MCP Server Boilerplate 改修指示書

## 1. Intent

既存のMCP Serverボイラープレートを改修し、FastMCPへの依存をアダプタ層へ限定する。

FastMCPをアプリケーションの中核基盤として直接利用する構成ではなく、MCPプロトコルとの接続を担当する外部境界アダプタとして扱う。

MCP Serverの業務ロジック、ユースケース、ドメインモデル、設定、監査ログ、テストコードがFastMCP固有APIへ直接依存しない構造を確立する。

生成された成果物はAriadne本体、aiwfctl、Ariadne Runtime、Dispatcher、RAGその他のAriadne構成要素へ依存せず、独立したリポジトリとして起動、試験、保守、デプロイできること。

------

## 2. Background

現行のMCP Serverボイラープレートでは、FastMCPのデコレータ、Context、Tool、Resource、Promptなどの概念がアプリケーション内部へ直接入り込む可能性がある。

この構造では、次の問題が発生する。

- FastMCPのAPI変更が業務ロジックへ波及する
- 公式MCP SDKや別実装への切り替えが困難になる
- Tool定義とユースケース実装の責務が混在する
- MCP以外のREST、CLI、gRPCなどの入口を追加しにくい
- 単体試験でFastMCPの起動環境が必要になる
- 生成成果物がAriadne固有構造へ依存する可能性がある
- 外部プロトコルとアプリケーション内部の境界が不明確になる

これを是正するため、Ports and Adapters、Hexagonal Architecture、Clean Architectureの考え方を参考に、FastMCP依存を外部アダプタ層へ隔離する。

------

## 3. Goal

次の責務分離を成立させる。

```text
MCP Client
    |
    v
FastMCP Adapter
    |
    v
Application Port
    |
    v
Application Use Case
    |
    v
Domain / Service
    |
    v
Outbound Port
    |
    v
Infrastructure Adapter
```

それぞれの責務は次のとおりとする。

### FastMCP Adapter

- MCP Tool、Resource、Promptの公開
- MCP入力値の受領
- 入力形式の検証
- FastMCP Contextから必要情報を抽出
- Application Portへ入力DTOを渡す
- Application ResultをMCP応答形式へ変換
- MCP固有例外への変換
- MCP Transportの起動

### Application Port

- 外部アダプタからアプリケーションを呼び出すための境界
- FastMCP型を受け取らない
- MCP、HTTP、CLIなどのプロトコルに依存しない
- Python標準型、独自DTO、Protocol、ABCのみを使用する

### Application Use Case

- ユースケースの実行制御
- 入力検証
- ドメインサービス呼び出し
- トランザクション境界
- 認可判断
- 出力DTO生成
- アプリケーション例外の送出

### Domain / Service

- 業務ルール
- ドメインモデル
- 値オブジェクト
- 業務判断
- 外部フレームワーク非依存

### Infrastructure Adapter

- DB
- ファイル
- HTTP API
- 外部サービス
- RAG
- ローカル推論モデル
- キュー
- キャッシュ
- その他外部I/O

------

## 4. Non-Goals

今回の改修では、次の内容は主目的としない。

- Ariadne Runtime自体へのMCP機能追加
- Ariadne DispatcherへのFastMCP組み込み
- Ariadne本体をMCP Serverとして公開すること
- FastMCPの独自Fork
- MCPプロトコルの独自実装
- Agent Runtimeの実装
- Discord Gatewayの実装
- MCP Clientの全面改修
- 特定業務向けToolの本実装
- 特定クラウドへの固定
- 特定LLMへの固定
- Ariadneへの実行時依存追加

ただし、将来のAgent Runtime、Discord Gateway、MCP Clientとの接続を妨げない境界設計とすること。

------

## 5. Core Principles

### 5.1 FastMCPを外部アダプタとして扱う

FastMCPはMCP通信を提供するライブラリであり、アプリケーションの中核ではない。

次の関係を維持する。

```text
Application Core
    does not know
FastMCP
```

Application、Domain、PortからFastMCPをimportしてはならない。

------

### 5.2 依存方向を内向きにする

依存方向は次のとおりとする。

```text
FastMCP Adapter
    -> Application Port
        -> Application Use Case
            -> Domain
```

DomainおよびApplicationからAdapterへ依存してはならない。

------

### 5.3 生成成果物を独立させる

生成されたMCP Serverプロジェクトは、Ariadneなしで次を実行できること。

```bash
uv sync
uv run pytest
uv run python -m app
```

または同等の標準的な起動方法を提供すること。

成果物内のソースコードから、次の名称をimportしてはならない。

- ariadne
- ariadne-runtime
- ariadne-dispatcher
- ariadne-rag
- aiwfctl

Ariadne固有の絶対パス、work ID、リポジトリ構成、環境変数を前提にしてはならない。

------

### 5.4 Framework型を内部へ持ち込まない

次のFastMCP固有要素をApplicationまたはDomainへ渡してはならない。

- FastMCP
- Context
- Tool
- Resource
- Prompt
- FastMCP固有Request
- FastMCP固有Response
- FastMCP固有Exception
- Transport固有オブジェクト

アダプタ内で独自DTOへ変換すること。

------

### 5.5 MCP以外の入口を追加可能にする

将来、次のアダプタを追加できる構造とする。

```text
adapters/inbound/
├── fastmcp/
├── cli/
├── rest/
├── grpc/
└── scheduler/
```

CLIやRESTから同じユースケースを呼び出す際、ApplicationおよびDomainの改修を不要とする。

------

## 6. Target Architecture

以下を標準構成の候補とする。

```text
mcp-server/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── Dockerfile
├── compose.yaml
├── src/
│   └── app/
│       ├── __init__.py
│       ├── __main__.py
│       ├── bootstrap.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py
│       │   └── logging.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── models/
│       │   ├── services/
│       │   ├── values/
│       │   └── exceptions.py
│       ├── application/
│       │   ├── __init__.py
│       │   ├── dto/
│       │   │   ├── requests.py
│       │   │   └── responses.py
│       │   ├── ports/
│       │   │   ├── inbound/
│       │   │   │   └── use_case_port.py
│       │   │   └── outbound/
│       │   │       └── repository_port.py
│       │   ├── use_cases/
│       │   │   └── execute_example.py
│       │   └── exceptions.py
│       ├── adapters/
│       │   ├── inbound/
│       │   │   └── fastmcp/
│       │   │       ├── __init__.py
│       │   │       ├── server.py
│       │   │       ├── tools/
│       │   │       │   └── example_tool.py
│       │   │       ├── resources/
│       │   │       │   └── example_resource.py
│       │   │       ├── prompts/
│       │   │       │   └── example_prompt.py
│       │   │       ├── mappers/
│       │   │       │   ├── request_mapper.py
│       │   │       │   ├── response_mapper.py
│       │   │       │   └── error_mapper.py
│       │   │       └── context/
│       │   │           └── request_context.py
│       │   └── outbound/
│       │       ├── memory/
│       │       │   └── repository.py
│       │       └── external_api/
│       │           └── client.py
│       └── observability/
│           ├── audit.py
│           ├── metrics.py
│           └── tracing.py
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   └── adapters/
│   ├── integration/
│   │   └── fastmcp/
│   ├── architecture/
│   │   └── test_dependency_rules.py
│   └── contract/
│       └── test_mcp_contract.py
├── docs/
│   ├── architecture.md
│   ├── dependency-rules.md
│   ├── adding-a-tool.md
│   ├── adding-an-adapter.md
│   └── deployment.md
└── scripts/
    ├── run.sh
    ├── run.ps1
    ├── test.sh
    └── test.ps1
```

ディレクトリ名は既存のAriadne boilerplate規約と整合させてよいが、責務境界は維持すること。

------

## 7. Required Refactoring

### 7.1 FastMCP Server生成処理を分離する

FastMCPインスタンスの生成は、次のいずれかへ限定する。

```text
adapters/inbound/fastmcp/server.py
```

または

```text
bootstrap.py
```

ただし、bootstrap.py内でFastMCP固有設定を直接大量に記述せず、FastMCP AdapterのFactoryを呼び出す構造を推奨する。

例：

```python
def create_application() -> ApplicationContainer:
    ...

def create_mcp_server(container: ApplicationContainer):
    ...
```

Application Containerの生成とFastMCP Serverの生成を分離すること。

------

### 7.2 Tool定義とUse Caseを分離する

FastMCP Tool内へ業務ロジックを書いてはならない。

禁止例：

```python
@mcp.tool()
def search_documents(query: str):
    records = database.search(query)
    ranked = rerank(records)
    return ranked
```

推奨例：

```python
@mcp.tool()
def search_documents(query: str):
    request = SearchDocumentsRequest(query=query)
    result = search_documents_use_case.execute(request)
    return map_search_result(result)
```

Toolは次の処理だけを担当する。

1. MCP入力を受け取る
2. DTOへ変換する
3. Use Caseを呼び出す
4. 結果をMCP応答へ変換する
5. 例外をMCPエラーへ変換する
6. 監査ログを記録する

------

### 7.3 Resource定義を分離する

Resource取得処理内へ、DBアクセスやファイル解析ロジックを直接記述しない。

Resource AdapterはApplication Portを呼び出し、結果をResource表現へ変換すること。

Resource URIの解析もアダプタ責務とし、内部へ生のFastMCP Resourceオブジェクトを渡さないこと。

------

### 7.4 Prompt定義を分離する

Prompt Templateとアプリケーションロジックを混在させない。

静的PromptはFastMCP Adapter内へ配置してよい。

動的Prompt生成で業務判断や外部データ取得が必要な場合は、Application Use Caseを介すること。

------

### 7.5 Request Contextを独自型へ変換する

FastMCP Contextから必要情報を抽出し、独自のRequestContextへ変換する。

例：

```python
@dataclass(frozen=True)
class RequestContext:
    request_id: str
    trace_id: str
    actor_id: str | None
    client_name: str | None
    metadata: Mapping[str, Any]
```

Application層はFastMCP Contextを参照してはならない。

取得できない値はNoneまたは明示的な既定値とし、外部ライブラリ仕様をApplicationへ漏らさない。

------

### 7.6 Error Mappingを分離する

例外は少なくとも次の3種類へ分ける。

```text
DomainException
ApplicationException
AdapterException
```

FastMCP固有エラーへの変換は、次のようなMapperへ集約する。

```text
adapters/inbound/fastmcp/mappers/error_mapper.py
```

Domain例外やApplication例外をFastMCP Tool内で個別に処理し続ける構成を避ける。

内部エラーの詳細、スタックトレース、秘密情報をMCPクライアントへ返さないこと。

------

### 7.7 Dependency Injectionを導入する

Use Case、Repository、External Client、Logger、Clock、ID GeneratorなどをDI可能にする。

グローバル変数へ直接依存しない。

FastMCP ToolからRepositoryを直接生成しない。

推奨構造：

```python
container = create_application_container(settings)
server = create_fastmcp_server(container)
```

DIライブラリの利用は必須としない。

シンプルなFactory、dataclass、Constructor Injectionを優先する。

------

## 8. Dependency Rules

以下の依存ルールを機械的に検証する。

### Allowed

```text
adapters -> application
adapters -> domain
application -> domain
bootstrap -> adapters
bootstrap -> application
bootstrap -> infrastructure
```

### Forbidden

```text
domain -> application
domain -> adapters
domain -> fastmcp
application -> adapters
application -> fastmcp
application -> transport
outbound adapter -> inbound adapter
```

特に次のimportを禁止する。

```python
# domain配下では禁止
from fastmcp import ...

# application配下では禁止
from fastmcp import ...
from app.adapters import ...
```

architecture test、import linter、AST解析などを利用し、自動検証すること。

------

## 9. Application Port Design

Inbound Portは、FastMCP固有概念を持たないインターフェースとする。

例：

```python
from typing import Protocol

class ExecuteExamplePort(Protocol):
    def execute(
        self,
        request: ExecuteExampleRequest,
        context: RequestContext,
    ) -> ExecuteExampleResponse:
        ...
```

同期または非同期のどちらを採用するかは、ボイラープレート全体で統一する。

外部I/Oを伴うMCP Serverではasyncを標準候補とする。

例：

```python
class ExecuteExamplePort(Protocol):
    async def execute(
        self,
        request: ExecuteExampleRequest,
        context: RequestContext,
    ) -> ExecuteExampleResponse:
        ...
```

同期処理と非同期処理を無計画に混在させないこと。

------

## 10. DTO Rules

DTOは次の条件を満たすこと。

- FastMCP型を使用しない
- Pydanticまたはdataclassのどちらかへ統一する
- RequestとResponseを分離する
- Domain Modelをそのまま外部へ公開しない
- 秘密情報をResponseへ含めない
- 入力値制約を明示する
- Optionalの意味を明確にする
- mutable defaultを使用しない

MCP Adapterでは、MCP入力からApplication DTOへの変換を行う。

Application DTOからMCP応答形式への変換もAdapter内で行う。

------

## 11. Logging and Audit

MCP呼び出しごとに、監査可能な構造化ログを出力する。

ログには最低限、次を含める。

```json
{
  "event": "mcp_tool_executed",
  "adapter": "fastmcp",
  "operation": "example_tool",
  "request_id": "request-id",
  "trace_id": "trace-id",
  "status": "success",
  "duration_ms": 12
}
```

入力値と出力値をログへ残す場合は、機密情報、認証情報、個人情報をマスキングする。

FastMCP AdapterのログとApplication Use Caseのログを区別できること。

例：

```text
mcp_request_received
application_use_case_started
application_use_case_completed
mcp_response_returned
```

AriadneのRuntimeログ形式を参考にしてよいが、Ariadne固有ライブラリへ依存してはならない。

------

## 12. Configuration

設定は環境変数および設定クラスへ集約する。

最低限、次の設定を扱えるようにする。

```text
APP_NAME
APP_ENV
LOG_LEVEL
MCP_TRANSPORT
MCP_HOST
MCP_PORT
MCP_PATH
REQUEST_TIMEOUT_SECONDS
```

必要に応じて次も追加する。

```text
AUTH_ENABLED
METRICS_ENABLED
TRACING_ENABLED
AUDIT_LOG_ENABLED
```

FastMCP設定値をApplicationやDomainから直接参照してはならない。

設定値はbootstrapまたはAdapter Factoryへ注入すること。

`.env.example`には秘密値を記載しない。

------

## 13. Transport Separation

stdio、HTTP、SSE、Streamable HTTPなど、利用可能なTransportが複数存在する場合、起動処理をAdapterまたはRunnerへ分離する。

例：

```text
adapters/inbound/fastmcp/transports/
├── stdio.py
└── http.py
```

Transport選択によってApplicationコードが変化しないこと。

Transport固有設定をDomainへ持ち込まないこと。

------

## 14. Test Requirements

### 14.1 Domain Unit Test

FastMCPを起動せず、業務ルールを試験できること。

------

### 14.2 Application Unit Test

RepositoryやExternal ClientをFakeまたはMockへ差し替え、Use Case単体で試験できること。

FastMCP Contextを使用してはならない。

------

### 14.3 FastMCP Adapter Unit Test

次を試験する。

- MCP入力からRequest DTOへの変換
- RequestContext変換
- Use Case呼び出し
- Response変換
- Domain例外の変換
- Application例外の変換
- 予期しない例外の安全な変換
- ログ出力
- 機密情報のマスキング

------

### 14.4 Integration Test

FastMCP Serverを起動し、少なくとも1つのToolをMCPクライアント相当から呼び出す。

次を確認する。

- Server起動
- Tool一覧取得
- Tool呼び出し
- 正常応答
- 不正入力応答
- 内部例外時の安全な応答
- Graceful Shutdown

------

### 14.5 Architecture Test

次を自動検証する。

- domainからfastmcpをimportしていない
- applicationからfastmcpをimportしていない
- applicationからadaptersをimportしていない
- FastMCP依存が指定ディレクトリ内へ限定されている
- Ariadne本体をimportしていない
- 絶対ローカルパスが存在しない

------

### 14.6 Contract Test

Tool名、引数、戻り値、エラー形式など、公開MCP Contractを試験する。

公開Toolの破壊的変更を検知できるようにする。

Tool Contractはドキュメントまたはスキーマとして管理する。

------

## 15. Sample Use Case

ボイラープレートには、責務分離を示す最小のサンプルToolを1つ含める。

例：

```text
echo_message
```

ただし、単なる文字列返却だけでは依存分離を確認しにくいため、次の流れを含めること。

```text
FastMCP Tool
    -> Request Mapper
    -> Application Use Case
    -> Domain Service
    -> Response Mapper
    -> MCP Response
```

サンプルは削除しやすく、実装規約の参考になる品質とする。

------

## 16. Bootstrap Design

起動処理は、次の順序を明示する。

```text
1. Load Settings
2. Configure Logging
3. Create Outbound Adapters
4. Create Application Use Cases
5. Create Application Container
6. Create FastMCP Adapter
7. Register Tools, Resources and Prompts
8. Start Selected Transport
9. Handle Shutdown
```

FastMCP Toolのimport時副作用で、ServerやDB接続が自動生成される構造を避ける。

テストから明示的にServerを生成できるFactoryを提供する。

------

## 17. Registration Design

Tool、Resource、Promptの登録方式を統一する。

候補：

```python
def register_tools(
    mcp: FastMCP,
    container: ApplicationContainer,
) -> None:
    register_example_tool(mcp, container.example_use_case)
```

または登録クラスを使用する。

自動探索を使用する場合も、暗黙的すぎる挙動を避け、登録対象を監査可能にする。

登録済みTool、Resource、Promptを起動時ログへ出力する。

------

## 18. Adding a New Tool

`docs/adding-a-tool.md`へ、次の追加手順を記載する。

1. Request DTOを作成する
2. Response DTOを作成する
3. Inbound Portを定義する
4. Use Caseを実装する
5. 必要ならOutbound Portを定義する
6. Infrastructure Adapterを実装する
7. FastMCP Request Mapperを実装する
8. FastMCP Response Mapperを実装する
9. Tool Adapterを実装する
10. Toolを登録する
11. Unit Testを追加する
12. Integration Testを追加する
13. Contract Testを追加する
14. READMEへ公開Toolを追記する

FastMCP Toolだけを追加し、Application層を経由しない実装を禁止する。

------

## 19. Adding Another Inbound Adapter

`docs/adding-an-adapter.md`へ、CLIやREST Adapter追加方法を記載する。

同一Use Caseを次のように再利用できることを示す。

```text
FastMCP Adapter ─┐
CLI Adapter ─────┼─> Application Use Case
REST Adapter ────┘
```

別Adapter追加時にFastMCP Adapterの修正を不要とする。

------

## 20. Security Requirements

最低限、次を実装または拡張可能にする。

- 入力値検証
- 最大文字数
- 最大配列件数
- タイムアウト
- 外部I/O制限
- パストラバーサル対策
- コマンドインジェクション対策
- SSRF対策
- 秘密情報マスキング
- エラー詳細の非公開化
- 認証情報の環境変数管理
- Toolごとの認可拡張ポイント
- 監査ログ
- Request ID
- Trace ID

シェル実行、ファイル操作、外部URLアクセスを行うサンプルを無制限に実装しない。

------

## 21. Graceful Shutdown

次のリソースを安全に終了できること。

- FastMCP Server
- HTTP Client
- DB Connection
- Queue Consumer
- Background Task
- Metrics Exporter
- Trace Provider

終了処理をFastMCP Adapterへ密結合させず、Application ContainerまたはLifecycle Managerで管理する。

------

## 22. Observability

ObservabilityはFastMCP固有実装へ閉じず、Applicationでも利用可能な抽象化を検討する。

ただし、過剰な抽象化は避ける。

最低限、次を計測できるようにする。

- MCP Tool呼び出し回数
- 成功件数
- 失敗件数
- 応答時間
- Use Case実行時間
- 外部I/O時間
- Timeout件数
- Validation Error件数

OpenTelemetry対応は任意機能として追加可能な構造とする。

------

## 23. Docker Requirements

Dockerイメージは単体で起動可能とする。

次を満たすこと。

- 非rootユーザー
- 不要パッケージを含めない
- Health Checkまたは起動確認手段
- 環境変数による設定
- 書き込み先を明示
- `.env`をイメージへ含めない
- Multi-stage buildの検討
- 依存バージョンを管理
- Ariadneのマウントを要求しない

------

## 24. CI Requirements

最低限、次をCIで実行する。

```text
format check
lint
type check
unit test
integration test
architecture test
contract test
dependency vulnerability scan
build
```

CI環境でもAriadne本体をcloneまたはinstallせずに成功すること。

------

## 25. Documentation Requirements

READMEへ最低限、次を記載する。

- プロジェクト概要
- FastMCPはInbound Adapterであること
- アーキテクチャ図
- ディレクトリ構成
- 起動方法
- テスト方法
- Docker起動方法
- Tool追加方法
- 別Adapter追加方法
- 設定一覧
- 公開Tool一覧
- セキュリティ上の注意
- Ariadne非依存であること
- FastMCP差し替え可能性
- 制約事項

`docs/architecture.md`には、依存方向と責務境界を明記する。

------

## 26. Migration Procedure

既存ボイラープレートを次の順序で改修する。

### Phase 1: Current-State Analysis

- FastMCP import箇所を列挙する
- Tool、Resource、Prompt内の業務ロジックを抽出する
- DB、外部API、ファイルI/Oへの直接依存を確認する
- グローバル状態を確認する
- Ariadne固有依存を確認する
- 起動処理と登録処理の副作用を確認する

分析結果をレポートとして残す。

------

### Phase 2: Boundary Definition

- Domain
- Application
- Inbound Port
- Outbound Port
- FastMCP Adapter
- Infrastructure Adapter
- Bootstrap

の境界を定義する。

依存関係図を作成する。

------

### Phase 3: Application Extraction

FastMCP Tool内の処理をUse Caseへ移動する。

FastMCP固有型を独自DTOへ置き換える。

外部I/OをOutbound Port経由へ変更する。

------

### Phase 4: FastMCP Adapter Construction

FastMCP Tool、Resource、Promptを薄いAdapterとして再実装する。

Mapper、Context変換、Error Mappingを追加する。

------

### Phase 5: Bootstrap Refactoring

Application Container生成とFastMCP Server生成を分離する。

import時副作用を除去する。

------

### Phase 6: Testing

Unit、Integration、Architecture、Contract Testを追加する。

既存機能の回帰試験を行う。

------

### Phase 7: Documentation

README、Architecture、Dependency Rules、追加手順を更新する。

------

### Phase 8: Evidence

改修前後の依存関係、テスト結果、起動結果、FastMCP依存箇所をEvidenceとして残す。

------

## 27. Acceptance Criteria

以下をすべて満たした場合に完了とする。

### Architecture

- FastMCP依存がInbound Adapter配下へ限定されている
- DomainからFastMCPをimportしていない
- ApplicationからFastMCPをimportしていない
- ApplicationからAdapterをimportしていない
- Tool内に主要な業務ロジックが存在しない
- Outbound I/OがPort経由になっている
- bootstrapとserver生成が分離されている

### Independence

- Ariadne本体をinstallせずに起動できる
- Ariadne本体をinstallせずに全試験が成功する
- Ariadne固有パスを参照していない
- Ariadne固有環境変数を要求しない
- 独立したGitリポジトリとして利用できる
- 独立したDockerイメージとして起動できる

### Extensibility

- FastMCP以外のInbound Adapterを追加可能
- 同じUse CaseをCLIなどから呼び出せる
- FastMCPを差し替えてもDomainとApplicationの改修が不要
- Transport変更でApplicationが変更されない

### Quality

- Unit Test成功
- Integration Test成功
- Architecture Test成功
- Contract Test成功
- Type Check成功
- Lint成功
- Docker Build成功
- README記載どおりに起動成功

### Security

- 入力値検証がある
- 内部例外をそのまま外部へ返さない
- 秘密情報がログへ出力されない
- タイムアウト設定がある
- 非rootコンテナで起動可能

------

## 28. Required Evidence

最低限、次のEvidenceを出力する。

```text
evidence/
├── current-fastmcp-dependencies.txt
├── refactored-fastmcp-dependencies.txt
├── dependency-graph-before.md
├── dependency-graph-after.md
├── architecture-test-result.txt
├── unit-test-result.txt
├── integration-test-result.txt
├── contract-test-result.txt
├── type-check-result.txt
├── lint-result.txt
├── docker-build-result.txt
├── standalone-startup-result.txt
└── acceptance-checklist.md
```

Evidenceには実行コマンド、終了コード、実行日時、対象バージョンを記録する。

------

## 29. Human Checkpoints

次のタイミングでHuman Checkを行う。

### Human Check 1: 境界設計確認

確認対象：

- FastMCP Adapterの責務
- Application Portの責務
- Domainの責務
- Outbound Adapterの責務
- 依存方向
- ディレクトリ構成

------

### Human Check 2: 公開Contract確認

確認対象：

- Tool名
- 引数
- 戻り値
- Resource URI
- Prompt名
- エラー形式
- 破壊的変更の有無

------

### Human Check 3: 独立性確認

確認対象：

- Ariadne依存の残存
- 独立起動
- 独立試験
- Docker単体起動
- READMEの再現性

------

## 30. Implementation Constraints

- 既存機能を不必要に削除しない
- 公開MCP Contractの破壊的変更を避ける
- 破壊的変更が必要な場合は理由と移行方法を提示する
- FastMCPの内部実装へ依存しすぎない
- 過剰な抽象化を避ける
- 1つのInterfaceに多数の責務を持たせない
- Toolごとに重複した例外処理を実装しない
- import時に外部接続を開始しない
- テスト専用分岐を本番コードへ大量に入れない
- ハードコードされたローカルパスを使用しない
- 秘密情報をソースコードへ記載しない
- Ariadne固有ライブラリを成果物へ追加しない

------

## 31. Expected Result

改修後のMCP Serverボイラープレートは、次の状態となる。

```text
Ariadne
    |
    | generates
    v
Independent MCP Server Project
    |
    ├── Application Core
    ├── Domain
    ├── FastMCP Inbound Adapter
    ├── Infrastructure Adapters
    ├── Tests
    ├── Docker
    └── Documentation
```

FastMCPはMCP接続を提供する交換可能なアダプタであり、Application Coreを支配しない。

生成成果物はAriadneから完全に独立し、単独で開発、試験、デプロイ、保守できる。

最終的に、次の原則をコード、試験、ドキュメントで証明すること。

> FastMCPにアプリケーションを載せるのではなく、アプリケーションへFastMCPを接続する。

------

## 32. Final Report

作業完了時は、次の形式で報告する。

```markdown
# FastMCP Adapter Separation Refactoring Report

## Summary

## Changed Files

## Architecture Before

## Architecture After

## FastMCP Dependency Scope

## Extracted Application Use Cases

## Dependency Rule Verification

## Standalone Execution Verification

## Test Results

## Contract Compatibility

## Security Verification

## Remaining Risks

## Deferred Items

## Evidence

## Acceptance Criteria Result
```

未完了項目、暫定対応、既知の制約を隠さず記載すること。