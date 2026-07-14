# Next.js Webapp Template

This is a reusable boilerplate for Next.js dashboard, admin, monitoring, and business web applications. Copy this directory to a new app repository or service directory, then edit only the copy.

## Purpose

- Provide a working Next.js App Router baseline.
- Keep TypeScript contracts visible from the first commit.
- Provide a generic dashboard shell without business-specific logic.
- Give later AI workflows clear extension points.

## Technology

- Next.js App Router
- React
- TypeScript
- lucide-react icons
- Vitest unit tests
- Playwright E2E tests
- Docker and Docker Compose

## Prerequisites

- Node.js 20.9 or newer
- npm
- Docker Desktop or compatible Docker runtime, when using Docker

## Quick Start

```powershell
npm install
npm run dev
```

Open `http://localhost:3000`.

## Health Check

```powershell
Invoke-RestMethod http://localhost:3000/api/health
```

Response shape:

```json
{
  "status": "UP",
  "service": "Sample Next.js App",
  "timestamp": "2026-01-01T00:00:00.000Z"
}
```

## Environment Variables

Copy `.env.example` to `.env.local` when local overrides are needed.

| Variable | Default | Purpose |
| --- | --- | --- |
| `NEXT_PUBLIC_APP_NAME` | `Sample Next.js App` | Display name and health service name |
| `NEXT_PUBLIC_APP_VERSION` | `0.1.0` | Footer version display |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:3000` | Browser-side API base URL |
| `NEXT_PUBLIC_POLLING_INTERVAL_MS` | `3000` | Default polling interval |
| `PORT` | `3000` | Runtime HTTP port |

## Directory Structure

```text
nextjs-app-template/
  README.md
  docs/
    requirements.md
    architecture.md
    ui-guideline.md
    operations.md
  app/
    layout.tsx
    page.tsx
    globals.css
    api/health/route.ts
  components/
    layout/
    common/
    dashboard/
  hooks/
    usePolling.ts
  lib/
    api-client.ts
    constants.ts
    types.ts
    format.ts
  config/
    app.config.example.json
  tests/
    unit/
    e2e/
  .env.example
  Dockerfile
  docker-compose.yml
  package.json
```

## Commands

```powershell
npm run typecheck
npm run lint
npm run test
npm run e2e
npm run build
```

## Docker

```powershell
docker compose up --build
```

Open `http://localhost:3000` or call `http://localhost:3000/api/health`.

## Extension Method

- Rename `NEXT_PUBLIC_APP_NAME` and update metadata.
- Replace sample metrics and events with product API data.
- Add feature modules after requirements define routes, user actions, API contracts, and authorization policy.
- Keep reusable UI under `components/common`.
- Keep product-specific UI under a feature folder or route segment.
- Keep API contract types in `lib/types.ts` until a domain-specific folder becomes clearer.

## AI Workflow Usage

Before extending this template, provide the AI workflow with:

- Product requirements and route map.
- Backend API contracts and error response shape.
- Auth/session policy.
- UI state and loading/error behavior.
- Unit, E2E, health, UI smoke, and API connectivity test expectations.
- Deployment target, environment variables, and secret ownership.

For repository workflow runs, create this preparation report before implementation:

```text
work/<receipt-id>/process-report/nextjs-webapp-implementation-prep.md
```

Template:

```text
templates/process-report/nextjs-webapp-implementation-prep-template.md
```

When a screen layout is provided as SVG, use the repository workflow to convert it into reviewed layout candidates before implementation:

```text
docs/workflows/web-svg-layout-mode.md
work/requirements/svg-input/WEB_SYS_<name>.svg
work/requirements/svg-input/WEB_FEAT_<name>.svg
work/requirements/svg-input/WEB_FIX_<name>.svg
```

## Guardrails

- Do not add business-specific logic to shared layout or common components.
- Do not hard-code production endpoints.
- Do not introduce external I/O in render-only components.
- Do not skip `/api/health` when deploying as a microservice.
