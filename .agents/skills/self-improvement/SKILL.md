---
name: self-improvement
description: Collect workflow feedback from Ariadne AI Workflow Platform runs, append human review decisions, generate GitHub Issue bodies for accepted feedback, create standard issue branch/evidence scaffolds, and hand off to existing GitHub/SCM helpers. Use when the user selects /self-improvement or asks to turn workflow friction, noise, repeated checks, missing context, docs ambiguity, runtime observation gaps, or workflow usability issues into a governed improvement flow.
---

# Self Improvement

この Skill は、Codex が `/self-improvement` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/self-improvement.prompt.md`
- `docs/workflows/self-improvement.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
