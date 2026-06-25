# UI Guideline

## Layout

- Use the existing header, sidebar, main content, and version footer shell.
- Keep repeated items as cards with `8px` border radius.
- Keep page sections as normal layout regions, not nested cards.
- Use dense but readable dashboard spacing for operational use.

## Components

- Use `StatusBadge` for service status.
- Use `LoadingState` and `ErrorState` for async states.
- Use `SummaryCard`, `MetricCard`, and `EventList` for the initial dashboard shape.
- Prefer icons from `lucide-react` for navigation and tool buttons.

## Accessibility

- Preserve semantic landmarks: `header`, `aside`, `nav`, `main`, and `footer`.
- Use headings in order.
- Keep contrast high for status and event badges.
- Add labels to interactive icon-only controls.

## Extension Rule

Do not encode business-specific labels, statuses, or workflows in shared components. Add those names in feature-level modules after requirements are approved.
