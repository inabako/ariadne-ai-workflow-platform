# Requirements

## Purpose

This template provides a reusable starting point for monitoring screens, admin screens, dashboards, and business web applications.

## Scope

- Use Next.js App Router.
- Use TypeScript.
- Provide a generic dashboard layout.
- Include a health check API.
- Avoid product-specific business logic.
- Keep extension points obvious for later AI workflow steps.

## Out Of Scope

- Authentication and authorization decisions.
- Product-specific API contracts.
- Database schema and persistence.
- Production observability backend selection.

## Acceptance Criteria

- `npm install` completes.
- `npm run dev` starts the app.
- `/api/health` returns JSON with `status`, `service`, and `timestamp`.
- The top page displays the app name, status, metrics, events, and extension points.
- Docker startup instructions are documented.
