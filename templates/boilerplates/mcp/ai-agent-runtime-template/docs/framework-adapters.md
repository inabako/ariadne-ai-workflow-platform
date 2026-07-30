# Framework Adapter Patterns

Framework adapter skeletons live under `src/local_agent_runtime/framework_adapters/`.

They intentionally do not import LangGraph, CrewAI, Microsoft Agent Framework, or AutoGen packages. Add those SDK dependencies only inside the matching adapter module when a generated project needs the framework.

## Expansion Order

```text
Common Runtime Contract
  -> Native baseline
  -> LangGraph adapter
  -> CrewAI adapter and Microsoft Agent Framework adapter
  -> AutoGen compatibility adapter
```

## Adapter Rules

- Convert `WorkflowRequest` into framework-owned execution state.
- Keep framework-native state in `framework_metadata`.
- Convert framework completion back into `WorkflowResult`.
- Do not expose framework state through Runtime Contract fields.
- Do not move Tool, Model, Human Check, or Evidence policy into the framework adapter.

## Current Skeletons

| Adapter | File | Responsibility |
| --- | --- | --- |
| LangGraph | `framework_adapters/langgraph.py` | Map Runtime Contract to graph state and back |
| CrewAI | `framework_adapters/crewai.py` | Map Runtime Contract to crew/task state and back |
| Microsoft Agent Framework | `framework_adapters/microsoft_agent_framework.py` | Map Runtime Contract to Microsoft agent orchestration state and back |
| AutoGen Compatibility | `framework_adapters/autogen_compat.py` | Convert AutoGen-style message flow into Runtime Contract results |
