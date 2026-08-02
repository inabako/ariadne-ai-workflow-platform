# Development Notes

このディレクトリは、Ariadne AI Workflow Platform の各versionで何を意図し、何を変更し、どの検証を行ったかを残す場所です。

Development Notes はrelease noteそのものではありません。Issue、Pull Request、commit、Feedback report、Runtime log、test evidenceを後から読み直すための運用記録です。

## 読む順番

| Version | Note | 主な内容 |
| --- | --- | --- |
| v0.0.1 | [v0.0.1.md](v0.0.1.md) | Context FirstなAI workflow基盤、初期runtime、RAG、Evidence、Human Check |
| v0.0.2 | [v0.0.2.md](v0.0.2.md) | Runtime復帰、Feedback、Review Council Runtime、Expectation-Driven Design Flow、OSS公開準備 |
| v0.0.3 | [v0.0.3.md](v0.0.3.md) | OSS公開後の運用安定化、Issue / PR template、registry bootstrap、Runtime trace / log |

## 書く内容

各version noteには、最低限次を残します。

- version / branch / baseline / status
- そのversionで達成したいGoal
- 主要な変更点と判断理由
- Runtime、Workflow、Knowledge、Docs、Test、Governanceへの影響
- 実施した検証
- 次versionへ送る改善候補

## 運用ルール

Development Notes は、会話ログの代替ではなく、後続Agentと人間が判断を再開するためのartifactです。

IssueやPull Requestでは作業単位を管理し、Development Notesではversion全体の意図、決定、検証、残課題を管理します。
