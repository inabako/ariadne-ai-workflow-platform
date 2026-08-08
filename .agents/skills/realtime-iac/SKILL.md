---
name: realtime-iac
description: Run the realtime-system Infrastructure as Code workflow for target systems, IoT, edge AI, video streaming, remote operation, or realtime gateway infrastructure. Use when the user selects /realtime-iac or asks to design, generate, review, test, and document IaC artifacts such as Docker Compose, systemd, firewall, reverse proxy, TURN/STUN, logrotate, monitoring, or runtime environment configuration.
---

# Realtime Iac

この Skill は、Codex が `/realtime-iac` を候補検出するための repo-local entrypoint です。

Workflow 定義はこの file に複製しません。Task action の前に、次を正本として読んでください。

- `.agents/skills/README.md`
- `AGENTS.md`
- `.ariadne/prompts/realtime-iac.prompt.md`
- `docs/workflows/realtime-iac.md`

Phase 順序、Human Check gate、artifact path、runtime command、stop condition は参照先に従ってください。
