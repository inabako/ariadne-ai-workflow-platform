# Semantic Commit Message Guideline

GitHub knowledge maintenance では、commit source を読み、GitHub の commit list だけでも変更意図が分かる semantic subject と、再利用可能な commit body を提案します。

## Subject

形式:

```text
type(scope): 変更の責務または成果
```

良い subject は、GitHub の commit list だけで以下が分かります。

- 何の領域を変えたか
- 何を可能にしたか
- どの責務や境界を明確にしたか
- 将来の AI workflow が再読すべき知識の anchor

推奨 type:

- `feat`: runtime behavior、機能、運用能力を追加した
- `fix`: 不具合、誤動作、危険な挙動を修正した
- `docs`: README、運用契約、設計説明、手順を更新した
- `chore`: build、ignore、metadata、非機能的な整理
- `refactor`: 外部挙動を変えずに責務分離や構造を改善した
- `test`: test、verification、evidence を追加した

scope は広すぎない名前にします。

避ける scope:

- repository 全体名だけ
- product 名だけ
- `misc`
- `update`

推奨 scope:

- `runtime`
- `supervisor`
- `protocol`
- `deployment`
- `docs`
- `safety`
- `telemetry`
- `video`
- `config`

避ける subject:

```text
feat(target-system): 対応
feat(target-system): 修正
feat(target-system): README.mdを修正
feat(target-system): protocol共通化に伴う対応
feat(target-system): 耐障害性向上のためプロセス分離対応
```

推奨 subject:

```text
docs(runtime): supervisor/worker運用契約とprotocol依存をREADMEへ反映
feat(supervisor): worker分離とcontrol安全境界を追加
feat(protocol): UDP port定義をtarget-system-protocolへ集約
```

## Body

body には、subject だけでは収まらない知識を残します。

必須観点:

- intent: なぜ変更したか
- scope: どの領域を変更したか
- decision: どの設計判断を採用したか
- impact: 運用、保守、互換性、安全性への影響
- future AI value: 将来の AI workflow が再利用すべき判断

安全境界、deployment contract、cross-repository dependency、protocol contract が関係する場合は body に明記します。

## Review Checklist

- subject は GitHub commit list だけで意味が通る。
- scope は repository 名や product 名だけでなく、責務領域を表している。
- 「修正」「対応」「更新」だけで終わっていない。
- body は intent、scope、decision、impact を説明している。
- commit source は変更しない。
- rewrite 時は before/after SHA mapping と tree hash 一致を記録する。
