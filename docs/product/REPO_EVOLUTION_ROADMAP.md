# Communication OS Repo Evolution Roadmap

## 1. Purpose

This document maps the Communication OS product spec onto the current repository and proposes a practical evolution path from the current demo architecture to a coherent product kernel.

## 2. Current Repository Mapping

### 2.1 Frontend

Current role:

- operator-facing console
- thread views
- approval flows
- replay UI
- mock-first product prototype

Relevant areas:

- `src/app`
- `src/components`
- `src/lib`

### 2.2 E1 Thread Core

Current role:

- thread domain model
- event store
- main REST API
- persistence and repository beginnings

Relevant areas:

- `src/myproj/core/domain`
- `src/myproj/core/services`
- `src/myproj/core/repositories`
- `src/myproj/api`
- `src/myproj/infra/db`

### 2.3 E2 Policy and Control

Current role:

- delegation semantics
- risk synthesis
- approval logic
- kill switch and policy evaluation

Relevant areas:

- `src/policy_control`

### 2.4 E3 Execution Fabric

Current role:

- external integrations
- action runtime
- action lifecycle state machine
- outbox/inbox style delivery and ingestion

Relevant areas:

- `backend/e3`

### 2.5 E5 Intelligence Layer

Current role:

- planning
- drafting
- risk classification assistance
- summarization

Relevant areas:

- `src/e5`

## 3. Current Architectural Problems

### 3.1 Product Concepts Are Present but Split

The repository already contains many correct future-facing primitives:

- thread
- event
- approval
- delegation
- risk
- action execution
- replay UI

However, they are split across module boundaries that do not yet tell one coherent product story.

### 3.2 E1 and E2 Are Conceptually One Kernel

`src/myproj` and `src/policy_control` are separated physically, but in product terms they form one kernel:

- thread state
- policy
- risk
- approval
- human control

This should become a single core package boundary.

### 3.3 E3 Should Remain Operationally Separate

E3 is meaningfully different:

- async execution
- external adapters
- idempotency
- delivery lifecycle
- queue and retry semantics

It should remain a separate process boundary even if its dependency and contract story is aligned with the core.

### 3.4 Product-Level Objects Are Still Underspecified

The codebase currently lacks first-class representations for:

- sender stack
- authority grants
- disclosure cards
- request-direct-human interrupts
- attention firewall decisions

These should become first-class product and domain objects.

## 4. Target End State

### 4.1 Core Runtime Shape

The target system should have four major layers:

- `Communication Core`
- `Execution Fabric`
- `Intelligence Layer`
- `Operator Console`

### 4.2 Communication Core

This is the merged E1 + E2 runtime.
It should own:

- identities
- relationships
- threads
- delegation
- approval
- policy
- risk orchestration
- replay/event log

### 4.3 Execution Fabric

This is E3.
It should own:

- action runs
- outbox/inbox
- adapter invocation
- delivery acknowledgements
- external event ingress

### 4.4 Intelligence Layer

This is E5.
It should own:

- planning
- drafting
- classification assistance
- summarization

### 4.5 Operator Console

This is the web app.
It should own:

- thread list and thread workspace
- approval inbox
- replay center
- relationship and authority configuration

## 5. Recommended Repository Shape

### 5.1 Short-Term Shape

Keep existing package names but move toward this conceptual structure:

- `src/myproj` becomes the product kernel
- `src/policy_control` becomes a compatibility layer or temporary facade
- `backend/e3` remains its own service
- `src/e5` remains its own service or callable layer

### 5.2 Medium-Term Shape

Move E2 code under `src/myproj` gradually.

Recommended package targets:

- `src/myproj/core/identity`
- `src/myproj/core/relationships`
- `src/myproj/core/threads`
- `src/myproj/core/governance`
- `src/myproj/core/approvals`
- `src/myproj/core/risk`
- `src/myproj/core/replay`

During the transition, keep import compatibility via re-export shims from `src/policy_control`.

### 5.3 Long-Term Shape

Rename product kernel only if needed after behavior stabilizes.
Do not lead with package rename churn before the domain boundary is stable.

## 6. Product-to-Code Mapping

### 6.1 Identity

Current anchor:

- `src/myproj/core/domain/principal.py`

Gaps:

- explicit agent affiliation
- organization-level identity
- sender stack composition
- disclosure defaults

### 6.2 Relationship

Current anchor:

- `src/myproj/core/domain/relationship.py`

Gaps:

- richer relationship classes
- stronger mapping into delegation defaults
- product-visible relationship console semantics

### 6.3 Delegation and Authority

Current anchor:

- `src/myproj/core/domain/thread.py`
- `src/policy_control/delegation`
- `src/policy_control/common/constants.py`

Gaps:

- first-class authority grant object
- per-relationship overrides
- disclosure policy coupling
- request-direct-human semantics

### 6.4 Approval

Current anchor:

- `src/policy_control/approval`
- frontend approval screens

Gaps:

- stronger coupling to sender stack
- clearer action preview contract
- organization and personal override rules

### 6.5 Replay

Current anchor:

- `src/myproj/core/domain/event.py`
- `src/myproj/core/services/event_store.py`
- replay frontend pages

Gaps:

- richer event schemas for policy and authority
- explicit replay views for responsibility chains
- dispute and correction workflow

### 6.6 Action Execution

Current anchor:

- `backend/e3/action_runtime`
- `backend/e3/api/v1/actions.py`

Gaps:

- standardized action envelope shared with core
- sender stack propagation into execution
- replay linkage back into core thread events

### 6.7 Planning and Drafting

Current anchor:

- `src/e5/core/planner`
- `src/e5/core/drafter`

Gaps:

- direct integration with core thread/action abstractions
- better explanation artifacts for replay
- clearer confidence and escalation hooks

## 7. Phased Roadmap

## Phase 1: Product Kernel Alignment

Goal:

Define the missing first-class objects required by the product spec without moving too much code yet.

Deliverables:

- sender stack schema
- authority grant schema
- disclosure model
- attention firewall decision schema
- action envelope shared between core and E3

Suggested file targets:

- add new domain models under `src/myproj/core/domain` or `src/myproj/core/contracts`
- add API schemas for sender stack and authority preview
- extend replay event payload contracts

Exit criteria:

- important actions can describe owner, delegate, author, approver, executor, and disclosure mode
- approval previews show a structured sender stack

## Phase 2: Merge E1 and E2 Into One Communication Core

Goal:

Eliminate the split between thread core and policy/control.

Deliverables:

- move policy, risk, approval, and delegation services under `src/myproj`
- leave `src/policy_control` as compatibility wrappers temporarily
- centralize shared enums and types

Suggested file strategy:

- migrate `src/policy_control/approval/*` into `src/myproj/core/approvals/*`
- migrate `src/policy_control/delegation/*` into `src/myproj/core/governance/*`
- migrate `src/policy_control/risk/*` into `src/myproj/core/risk/*`
- migrate `src/policy_control/kill_switch/*` into `src/myproj/core/governance/*`

Exit criteria:

- core thread, policy, approval, and risk flows live under one package boundary
- API routes no longer reach into `policy_control` separately for product-critical decisions

## Phase 3: Replace In-Memory API State With Repository-Backed Core Flows

Goal:

Make all core route families use consistent persistence and service orchestration.

Deliverables:

- repositories for messages
- repositories for principals
- repositories for relationships
- repository-backed event retrieval
- removal of module-level mutable dictionaries

Suggested file targets:

- `src/myproj/api/v1/messages.py`
- `src/myproj/api/v1/principals.py`
- `src/myproj/api/v1/relationships.py`
- `src/myproj/api/v1/events.py`
- new repository modules under `src/myproj/core/repositories`

Exit criteria:

- all route families share one persistence story
- replay and thread data remain consistent across endpoints

## Phase 4: Integrate Core and E3 Via A Shared Action Contract

Goal:

Turn E3 from a sidecar demo into a clean execution fabric for the core.

Deliverables:

- shared action request and result contract
- thread-originated actions in core create or reference `ActionRun`
- E3 execution results append events back into core
- unified idempotency semantics across request path

Suggested file targets:

- `backend/e3/api/v1/actions.py`
- `backend/e3/action_runtime/models.py`
- `src/myproj/core/services/thread_service.py`
- new shared contracts package under `src/myproj/core/contracts`

Exit criteria:

- action planning and action execution are one coherent lifecycle
- replay can show both decision and delivery sides

## Phase 5: Strengthen Replay, Accountability, and Human Rights

Goal:

Make replay and human control product-grade rather than demo-grade.

Deliverables:

- richer event taxonomy for authority, disclosure, and approval
- request-human interrupts
- revoke delegation flows
- dispute or correction markers in replay

Suggested file targets:

- `src/myproj/core/domain/event.py`
- `src/myproj/core/services/event_store.py`
- frontend replay components
- approval UI and thread workspace

Exit criteria:

- users can understand why an action happened
- users can interrupt or reclaim control clearly

## Phase 6: Build The True Operator Console

Goal:

Evolve the frontend from prototype screens into a coherent operations product.

Deliverables:

- unified thread workspace
- approval inbox as a first-class control center
- relationship console
- identity and authority console
- attention firewall view

Suggested frontend targets:

- `src/app/(app)/threads`
- `src/app/(app)/approvals`
- `src/app/(app)/replay`
- new `src/app/(app)/relationships`
- new `src/app/(app)/authority`

Exit criteria:

- the UI tells a coherent product story that is about threads, delegation, approval, and replay rather than generic chat

## Phase 7: Add Federation and Multi-Organization Semantics

Goal:

Support communication across organizational and personal agent boundaries.

Deliverables:

- external authority cards
- organization agent identities
- inter-tenant sender stack verification
- stronger disclosure policies

This phase should not begin until the internal product kernel is coherent.

## 8. Immediate Next Backlog

### 8.1 Highest-Leverage Domain Additions

- define `AuthorityGrant`
- define `SenderStack`
- define `DisclosurePolicy`
- define `AttentionDecision`
- define `ActionEnvelope`

### 8.2 Highest-Leverage Refactors

- unify route persistence paths
- start moving E2 modules under `src/myproj`
- standardize event payloads for policy and approval

### 8.3 Highest-Leverage UI Work

- redesign thread detail around action and replay
- make approval inbox richer than a simple list
- expose sender stack preview in approval cards

## 9. Suggested File-Level Plan

### 9.1 New Domain Modules

Recommended additions:

- `src/myproj/core/domain/authority.py`
- `src/myproj/core/domain/disclosure.py`
- `src/myproj/core/domain/attention.py`
- `src/myproj/core/contracts/actions.py`

### 9.2 Core Merge Targets

Recommended landing zones:

- `src/myproj/core/governance/`
- `src/myproj/core/approvals/`
- `src/myproj/core/risk/`

### 9.3 Compatibility Strategy

For a period, keep:

- `src/policy_control/...` re-exporting from `src/myproj/...`

This avoids breaking imports while the kernel merge lands.

## 10. Testing Strategy For The Roadmap

### 10.1 Contract Tests

Add tests that guarantee:

- sender stack serialization is stable
- action envelope contracts remain compatible between core and E3
- replay events include authority and approval metadata

### 10.2 Integration Tests

Add:

- thread -> approval -> E3 execution -> replay flows
- relationship-specific delegation enforcement tests
- revoke and take-over tests

### 10.3 UI Tests

Add:

- approval preview tests
- replay interpretation tests
- request-human interrupt behavior tests

## 11. Risks and Mitigations

### 11.1 Risk: Premature Package Renames

Mitigation:

- merge behavior before renaming everything

### 11.2 Risk: E3 Becomes Too Coupled

Mitigation:

- share contracts, not runtime state
- keep process boundary even if package tooling is aligned

### 11.3 Risk: Product Vision Outpaces Operational Reliability

Mitigation:

- keep narrow scenarios
- require replay and approvals before broader automation

### 11.4 Risk: Frontend Reverts To Chat Metaphor

Mitigation:

- keep thread, action, replay, and approval as the primary UI primitives

## 12. Recommended Sequence Of Work

1. Introduce sender stack and authority grant models.
2. Start E1 + E2 logical merge under `src/myproj`.
3. Replace remaining in-memory route state with repositories.
4. Define shared action envelopes between core and E3.
5. Make replay and approval product-grade.
6. Expand the frontend into a true operator console.

## 13. Summary

The repository already contains the seeds of a future-facing Communication OS.
The highest-value move is not to build more chat features.
It is to unify the existing thread, policy, approval, risk, replay, and execution pieces into one coherent communication kernel with a separate execution fabric.

If this roadmap is followed, the project can evolve from a promising demo into the core runtime for delegated communication in a mixed human-agent world.
