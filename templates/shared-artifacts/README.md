# Shared Artifacts Templates

Shared Artifacts are the handoff boundary between the new robotics system workflow and the realtime IaC workflow.

They are the single source of truth for IaC. The IaC workflow must not invent missing ports, routes, software, public exposure, or ownership boundaries.

## Templates

| Template | Purpose |
| --- | --- |
| `shared-artifacts-index-template.md` | Lists all Shared Artifacts and validator status. |
| `port-definition-template.md` | Defines ports, protocols, owners, exposure, bind address, and test mapping. |
| `network-boundary-definition-template.md` | Defines zones, allowed/blocked flows, enforcement points, and evidence. |
| `architecture-decision-record-template.md` | Records architecture / infrastructure decisions, reasons, alternatives, and IaC impact. |

Related templates:

```text
templates/iac/communication-specification-template.md
templates/iac/software-inventory-template.md
```
