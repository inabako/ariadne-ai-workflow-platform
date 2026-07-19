# Operations

## Local Commands

Prerequisite: Node.js 20.9 or newer.

```powershell
npm install
npm run dev
npm run typecheck
npm run lint
npm run test
npm run e2e
```

## Unit Test Policy

Unit tests should cover pure formatting, state transition helpers, API client behavior with mocks, and component rendering that does not require real external services.

## E2E Test Policy

E2E tests should cover the top page, the health endpoint, route-level access rules, and the main user workflow after product requirements are added.

## Health Check

```powershell
Invoke-RestMethod http://localhost:3000/api/health
```

Expected shape:

```json
{
  "status": "UP",
  "service": "Sample Next.js App",
  "timestamp": "2026-01-01T00:00:00.000Z"
}
```

## UI Smoke Test

- Start the app with `npm run dev`.
- Open `http://localhost:3000`.
- Confirm the app name, status badge, sample metrics, sample events, and extension points render.

## API Connectivity Check

Use `/api/health` as the first API connectivity check. Add feature-specific API checks only after the backend contract exists.

## Docker

```powershell
docker compose up --build
```

Then open `http://localhost:3000` or call `http://localhost:3000/api/health`.
