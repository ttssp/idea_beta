# Parallel Engineering Plans

## 1. Can This Be Parallelized?

Yes.
The next phase can be split into parallel workstreams, but not from minute zero.

The work should follow this structure:

1. freeze contracts and ownership boundaries
2. run 4-6 independent workstreams in parallel
3. use one lead integrator to merge the seams

The highest-risk failure mode is not coding difficulty.
It is uncontrolled overlap on shared files and object definitions.

## 2. Recommended Team Shape

Recommended staffing:

- 1 lead/integrator
- 5 implementation engineers
- optional 1 intelligence-layer engineer if extra capacity exists

If the team is smaller, combine Engineer 1 and Engineer 3 first.

## 3. Shared Rules Before Parallel Work Starts

All engineers should follow these rules:

- do not redefine sender stack semantics locally
- do not edit another engineer's owned write scope unless the lead explicitly reassigns it
- do not change shared API field names ad hoc
- do not collapse thread/action/replay semantics back into generic message semantics
- all major contracts must ship with tests and example payloads

## 4. Dependency Map

### Hard prerequisite

Lead + Engineer 1 must freeze:

- `AuthorityGrant`
- `SenderStack`
- `DisclosurePolicy`
- `AttentionDecision`
- `ActionEnvelope`

Only after that should the rest of the team begin implementation branches.

### Parallelizable after freeze

- Engineer 2: repositories + route migration
- Engineer 3: governance merge
- Engineer 4: E3 action fabric
- Engineer 5: frontend operator console
- Optional Engineer 6: E5 intelligence integration

### Final integration

Lead merges and reconciles:

- contract exports
- end-to-end flows
- test gaps
- UI/backend schema mismatches

## 5. Write-Scope Assignment

## Lead / Integrator

Primary responsibility:

- contract freeze
- merge order
- end-to-end integration
- conflict resolution

Owned write scope:

- `docs/product/*`
- shared export glue only when necessary
- final integration patches across multiple slices

Should avoid owning:

- large feature implementations inside one workstream

Success criteria:

- teams can work independently without redefining the system
- final integrated thread -> approval -> execution -> replay flow works

## Engineer 1: Core Contracts Engineer

Mission:

- define the new first-class product contracts that the rest of the system will build on

Owned write scope:

- `src/myproj/core/contracts/**`
- `tests/unit/contracts/**`

Suggested deliverables:

- `authority.py`
- `sender_stack.py`
- `disclosure.py`
- `attention.py`
- `actions.py`

Key tasks:

- define data shapes and invariants
- add serializer tests
- write example payload fixtures for frontend and E3 consumption

Must not edit:

- `backend/e3/**`
- frontend pages/components
- API routes except for tiny type-only wiring approved by the lead

Dependencies:

- none

Primary tests:

- unit tests for model validation and serialization

Handoff to others:

- frozen example JSON payloads
- field naming rules
- authority semantics cheat sheet

## Engineer 2: Core Persistence And API Engineer

Mission:

- eliminate in-memory route state and make the core runtime repository-backed

Owned write scope:

- `src/myproj/core/repositories/**`
- `src/myproj/infra/db/models.py`
- `src/myproj/api/v1/messages.py`
- `src/myproj/api/v1/principals.py`
- `src/myproj/api/v1/relationships.py`
- `src/myproj/api/v1/events.py`
- `tests/conftest.py`
- `tests/unit/test_api_endpoints.py`

Key tasks:

- add message/principal/relationship/event repositories
- map entities to persistence layer
- remove module-level dictionaries and singleton mutable state
- migrate routes to injected repositories/services

Must not edit:

- `src/policy_control/**`
- `backend/e3/**`
- frontend code

Dependencies:

- can start in parallel after contract freeze

Primary tests:

- repository tests
- API integration tests
- regression tests for consistency across routes

Acceptance criteria:

- all core route families use the same persistence story
- replay data and thread data stay consistent

## Engineer 3: Governance Kernel Engineer

Mission:

- merge E2 behavior into `src/myproj` without breaking compatibility

Owned write scope:

- `src/myproj/core/governance/**`
- `src/myproj/core/approvals/**`
- `src/myproj/core/risk/**`
- `src/policy_control/**`

Key tasks:

- create landing zones under `src/myproj`
- move delegation, approval, policy, risk, and kill-switch logic gradually
- leave re-export shims in `src/policy_control`
- align shared enums and types with the frozen contracts

Must not edit:

- `src/myproj/api/v1/**`
- `backend/e3/**`
- frontend code

Dependencies:

- Engineer 1 contract freeze

Primary tests:

- unit tests for delegation, approval, risk, and policy flows
- compatibility tests ensuring old imports still work during transition

Acceptance criteria:

- governance logic can be called from `src/myproj` directly
- `src/policy_control` becomes a thin compatibility shell rather than the real product kernel

## Engineer 4: Execution Fabric Engineer

Mission:

- align E3 with the new shared action contract and replay requirements

Owned write scope:

- `backend/e3/**`
- `backend/e3/tests/**`

Key tasks:

- replace ad hoc request parsing with `ActionEnvelope`-aligned handling
- propagate sender stack and authority metadata through action runtime
- emit execution results that the core can map into replay events
- preserve idempotency and delivery correctness

Must not edit:

- `src/myproj/api/v1/**`
- `src/policy_control/**`
- frontend code

Dependencies:

- Engineer 1 contract freeze

Primary tests:

- `backend/e3/tests`
- contract compatibility tests if added

Acceptance criteria:

- E3 accepts a stable shared action shape
- execution and delivery milestones can be reflected back into replay

## Engineer 5: Frontend Operator Console Engineer

Mission:

- evolve the web app from a demo UI into a true operator console

Owned write scope:

- `src/app/(app)/threads/**`
- `src/app/(app)/approvals/**`
- `src/app/(app)/replay/**`
- `src/app/(app)/settings/**`
- `src/components/approval/**`
- `src/components/replay/**`
- `src/components/thread/**`
- `src/lib/types/**`
- `src/lib/api/**`

Key tasks:

- redesign thread detail as a workspace
- enrich approval inbox and approval detail views
- show sender stack and disclosure previews
- upgrade replay to show responsibility stages
- add relationship and authority management scaffolding screens

Must not edit:

- `backend/e3/**`
- `src/policy_control/**`
- repository and DB files

Dependencies:

- Engineer 1 for contract examples
- can prototype against stable mock payloads before backend integration lands

Primary tests:

- lint
- typecheck
- component and integration tests for approval/replay flows

Acceptance criteria:

- the UI tells a thread/action/approval/replay story clearly
- sender stack and authority are visible to operators

## Optional Engineer 6: Intelligence Layer Engineer

Mission:

- align E5 planning and drafting outputs with the new action and replay model

Owned write scope:

- `src/e5/**`
- web tests that exercise E5-facing flows if needed

Key tasks:

- emit structured action recommendations aligned to `ActionEnvelope`
- include explanation artifacts suitable for replay
- attach confidence and escalation metadata

Must not edit:

- `backend/e3/**`
- governance merge files unless approved

Dependencies:

- Engineer 1 contract freeze

Primary tests:

- E5 unit tests
- typecheck and web tests where relevant

Acceptance criteria:

- planner and drafter outputs become easy to consume by the core and UI

## 6. Delivery Order

### Sprint 0: 2-3 days

Lead + Engineer 1:

- freeze contracts
- publish examples
- lock write scopes

### Sprint 1: 5-7 days

Parallel:

- Engineer 2 builds repositories and route migration
- Engineer 3 builds governance landing zones and migrations
- Engineer 4 updates E3 action handling
- Engineer 5 upgrades UI against frozen examples
- Optional Engineer 6 aligns E5 outputs

### Sprint 2: 3-5 days

Lead-driven integration:

- merge branches
- resolve schema mismatches
- add end-to-end tests
- polish replay and approval seams

## 7. Merge Strategy

Recommended merge order:

1. Engineer 1 contracts
2. Engineer 3 governance landing zones
3. Engineer 2 repositories and API migration
4. Engineer 4 E3 action contract changes
5. Engineer 5 frontend integration
6. Optional Engineer 6 E5 integration
7. Lead final integration branch

Reason:

- contracts first
- core semantics next
- persistence before UI wiring
- execution fabric before end-to-end replay

## 8. Concrete Engineer Plans

## Lead / Integrator Plan

Week objectives:

- finalize object semantics
- keep teams unblocked
- own final integrated acceptance demo

Checklist:

- produce contract review notes
- approve example payloads
- review branch boundaries daily
- maintain integration branch
- own end-to-end acceptance criteria and demos

## Engineer 1 Plan

Week objectives:

- land the frozen contracts package
- document examples for all downstream teams

Checklist:

- implement contracts
- add unit tests
- create JSON examples in tests or fixtures
- hand over field dictionary to all engineers

## Engineer 2 Plan

Week objectives:

- remove demo-style mutable API state
- establish repository-backed flow for non-thread route families

Checklist:

- implement repositories
- add persistence mapping
- migrate route handlers
- add regression tests

## Engineer 3 Plan

Week objectives:

- create the future home for governance logic
- reduce architectural split between E1 and E2

Checklist:

- create governance packages
- move core logic
- preserve compatibility shims
- align tests

## Engineer 4 Plan

Week objectives:

- make E3 compatible with shared contracts and replay expectations

Checklist:

- map incoming action envelope
- carry sender stack through execution lifecycle
- emit replay-friendly execution outputs
- keep E3 tests green

## Engineer 5 Plan

Week objectives:

- make the product visually and conceptually read as a Communication OS

Checklist:

- redesign thread detail
- enrich approval cards/details
- improve replay timeline
- add authority/relationship management stubs

## Optional Engineer 6 Plan

Week objectives:

- make E5 outputs structured and replay-aware

Checklist:

- align planner output to action envelope
- align drafter output to sender stack/disclosure needs
- include explanation fields for replay

## 9. Main Parallelization Constraints

These areas should remain single-owner until integration:

- contract field definitions
- shared exports
- `src/myproj/infra/db/models.py`
- approval payload schema
- replay event payload schema

If multiple engineers need changes there, route them through the lead.

## 10. Summary

This phase is parallelizable if and only if:

- contracts freeze first
- write scopes stay disjoint
- one lead owns integration

With those conditions, 5 engineers can move quickly in parallel, and 6 engineers can do even more if E5 integration is included.
