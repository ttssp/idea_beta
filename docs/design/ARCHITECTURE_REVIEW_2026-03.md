# Architecture Review

## Summary

This repository is now in a much healthier state operationally: Python lint passes, core Python tests pass, E3 tests pass, and the frontend typecheck/tests pass. The next engineering gains are no longer about syntax or broken entry points; they are about reducing structural drift between modules.

## High-Risk Findings

### 1. Split data sources create inconsistent behavior

The `src/myproj` API layer mixes database-backed flows with in-memory stores:

- `threads` routes use `ThreadRepository`
- `events` uses a module-level `ThreadService`
- `messages`, `principals`, and `relationships` still use module-level dictionaries

Impact:

- API behavior depends on which route family you hit
- writes in one route may not be visible in another route
- productionizing these endpoints will be fragile because tests currently rely on in-process state reset

Recommendation:

- define repository interfaces for `Message`, `Principal`, `Relationship`, and `ThreadEvent`
- move all route handlers to dependency-injected repositories/services
- remove module-level singleton state from API modules

### 2. Python dependency management is fragmented

The root project uses `pyproject.toml` with Hatch, while `backend/e3` uses Poetry and also ships a separate `requirements.txt`.

Impact:

- dependency drift is likely
- local setup and CI can silently diverge
- cross-project upgrades are harder than they need to be

Recommendation:

- pick one canonical dependency source per Python subproject
- short term: keep `backend/e3/requirements.txt` as the execution source and treat Poetry metadata as descriptive only, or remove the duplicated file
- medium term: convert `backend/e3` to a standard `pyproject.toml` workflow aligned with the root project

### 3. Domain logic and API mutation logic are still partially duplicated

We fixed a large amount of this already, but duplication still exists as a pattern risk:

- route handlers still coordinate some mutation sequences directly
- version/timestamp semantics are spread across domain methods and service/repository layers

Impact:

- future features can easily reintroduce double version increments or inconsistent timestamps
- domain invariants are easier to bypass than they should be

Recommendation:

- keep mutations inside domain/service methods only
- make route handlers orchestration-only
- add repository/service integration tests for mutation semantics

## Medium-Risk Findings

### 4. E3 adapter tests validate interface behavior, but adapters are still thin wrappers over vendor SDKs

This is good for now, but the adapters have limited abstraction around retries, tracing, and error normalization.

Recommendation:

- introduce a shared adapter result/error envelope
- centralize vendor exception mapping in one place per adapter family

### 5. CI currently verifies correctness, but not packaging integrity

The new CI covers lint, tests, and frontend checks. It does not yet verify:

- root package install from a clean environment beyond editable mode
- production build behavior for Next.js
- alembic migration health

Recommendation:

- add a later CI stage for `npm run build`
- add a migration smoke test once a disposable database service is wired in

## Suggested Execution Order

1. Unify all `src/myproj` API routes behind repositories/services.
2. Consolidate Python dependency management strategy.
3. Add integration tests around repository-backed API behavior.
4. Expand CI to include build and migration smoke checks.

## Desired End State

The target architecture should look like this:

- API routes: thin transport adapters
- services: orchestration and policy
- domain models: invariants and state transitions
- repositories: all persistence concerns
- no module-level mutable API state
- one reproducible install story per Python project
