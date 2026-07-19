# Architecture

## Runtime Shape

The template uses Next.js App Router with a small dashboard surface and one Route Handler:

- `app/layout.tsx`: root HTML and metadata.
- `app/page.tsx`: initial dashboard screen.
- `app/api/health/route.ts`: health check endpoint.
- `components/layout`: shell, header, and sidebar composition.
- `components/common`: reusable status, loading, and error states.
- `components/dashboard`: dashboard-specific display components.
- `hooks`: client-side reusable hooks.
- `lib`: shared types, constants, formatting, and API clients.

## Boundary Rules

- Keep route handlers focused on HTTP request and response behavior.
- Keep UI components free of product-specific business rules.
- Put reusable data contracts in `lib/types.ts`.
- Put service-specific API clients in `lib/` or a dedicated feature folder.
- Add feature folders only after requirements identify a stable domain boundary.

## AI Workflow Handoff

When a later workflow extends this template, provide these decisions before coding:

- Product name and user roles.
- API contracts and error response rules.
- Auth/session policy.
- Required screens and route map.
- Test evidence requirements.
- Deployment target and environment variable ownership.
