# Dependency Rules

## Allowed

- `adapters -> application`
- `adapters -> domain`
- `application -> domain`
- `bootstrap -> adapters`
- `bootstrap -> application`

## Forbidden

- `domain -> application`
- `domain -> adapters`
- `domain -> fastmcp`
- `application -> adapters`
- `application -> fastmcp`
- `application -> transport`
- `outbound adapter -> inbound adapter`

## Mechanical Guard

The template includes an architecture test that scans source files and fails if `fastmcp` appears outside:

```text
src/local_model_mcp/adapters/inbound/fastmcp/
```

Add more import-boundary checks when the generated project grows.
