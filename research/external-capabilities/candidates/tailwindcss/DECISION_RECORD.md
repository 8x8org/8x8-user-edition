# MSG197-TAILWIND-001 Frontend Stack Decision

## Decision

`DEFER_NO_APPROVED_REQUIREMENT`

The current public User Edition is intentionally static and auditable. No package manifest is present in the current repository, and the existing public slices already use plain HTML, CSS and JavaScript with strict public/private boundaries.

Tailwind can be useful for design-token consistency and large component libraries, but adopting it now would create a build toolchain, dependency-update surface, generated-CSS governance burden and migration work without a named product requirement that the existing static stack cannot satisfy.

## Reopen conditions

Reopen only when a specific client needs component-scale theming or utility composition, a stable release is selected, an operational owner exists, bundle and build budgets are measured, WCAG regression tests pass, CSP remains strict and rollback to static CSS is rehearsed.

No package installation or frontend migration is authorized.
