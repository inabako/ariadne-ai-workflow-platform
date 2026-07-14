# Command Design

Initial commands use `/agent` as the root:

- `/agent submit`
- `/agent status`
- `/agent pause`
- `/agent resume`
- `/agent cancel`
- `/agent artifacts`
- `/agent health`

Commands map to Runtime Command DTOs and do not mutate runtime state directly inside the Gateway.

