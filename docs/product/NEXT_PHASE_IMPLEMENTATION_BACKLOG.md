# Next-Phase Implementation Backlog

## 1. Goal

The next phase should turn the current demo into a coherent Communication OS kernel by doing three things:

- define the missing product-critical domain objects
- unify the core runtime around thread + governance + approval + replay
- connect the core runtime to the execution fabric and operator console cleanly

This is not yet the full product.
It is the phase that creates a stable foundation for the product.

## 2. Release Objective

At the end of this phase, the repository should support one coherent end-to-end story:

1. a user opens a thread
2. the system determines relationship and delegation context
3. an action is prepared with a legible sender stack
4. policy and risk decide whether to auto-run, request approval, or escalate
5. the action executes through E3
6. the full chain is replayable in the UI

## 3. Definition Of Done

The phase is complete when all of the following are true:

- `AuthorityGrant`, `SenderStack`, `DisclosurePolicy`, `AttentionDecision`, and `ActionEnvelope` exist as first-class contracts
- `src/myproj` can host governance behavior now split across E1 and E2
- `messages`, `principals`, `relationships`, and `events` no longer rely on module-level mutable state
- approval previews include sender stack and action impact information
- E3 consumes a shared action contract instead of an ad hoc request shape
- replay can show authority, approval, and execution milestones
- the frontend tells a thread/action/approval/replay story rather than a chat-only story

## 4. Phase Structure

## Phase 0: Contract Freeze

Purpose:

- lock the product and engineering vocabulary before parallel implementation begins

Outputs:

- sender stack schema
- authority grant schema
- disclosure policy schema
- attention decision schema
- action envelope schema
- acceptance examples for each

Repo targets:

- `docs/product/COMMUNICATION_OS_V1_SPEC.md`
- `docs/product/REPO_EVOLUTION_ROADMAP.md`
- new domain/contracts modules under `src/myproj/core`

Exit criteria:

- all teams can code against the same object definitions
- no open ambiguity about owner/delegate/author/approver/executor semantics

## Phase 1: Product Kernel Foundations

Purpose:

- introduce the missing domain objects and landing zones without major behavior rewrites yet

P0 backlog:

### B001. Create shared contracts package

Deliver:

- `src/myproj/core/contracts/authority.py`
- `src/myproj/core/contracts/disclosure.py`
- `src/myproj/core/contracts/attention.py`
- `src/myproj/core/contracts/actions.py`
- `src/myproj/core/contracts/sender_stack.py`

Acceptance:

- contracts are importable from a stable package
- unit tests verify serialization and invariants

Dependencies:

- none

### B002. Add governance landing zones inside `src/myproj`

Deliver:

- `src/myproj/core/governance/`
- `src/myproj/core/approvals/`
- `src/myproj/core/risk/`

Acceptance:

- package structure exists
- initial services and types are migrated or shimmed

Dependencies:

- B001 for shared contracts

### B003. Define event payload conventions for replay

Deliver:

- event payload schema guidance
- authority/approval/execution payload shapes

Acceptance:

- replay-critical events have stable payload keys
- tests cover serialization and replay reconstruction assumptions

Dependencies:

- B001

## Phase 2: Persistence And Core API Unification

Purpose:

- replace demo-style mutable state with repository-backed runtime behavior

P0 backlog:

### B010. Add repository interfaces and implementations

Deliver:

- `MessageRepository`
- `PrincipalRepository`
- `RelationshipRepository`
- `EventRepository`

Acceptance:

- repositories exist under `src/myproj/core/repositories`
- route families can be migrated away from module dictionaries

Dependencies:

- none

### B011. Extend DB models and mapping layer

Deliver:

- persistence support for messages, principals, relationships, and events

Acceptance:

- database models represent the new core entities sufficiently for API flows
- repository tests pass

Dependencies:

- B010

### B012. Migrate route families to injected repositories/services

Deliver:

- `messages`, `principals`, `relationships`, and `events` routes no longer use module-level state

Acceptance:

- route behavior is consistent across process restarts
- tests do not rely on in-memory resets

Dependencies:

- B010
- B011

## Phase 3: Governance Merge

Purpose:

- make E1 and E2 one logical runtime

P0 backlog:

### B020. Move delegation services into `src/myproj`

Deliver:

- delegation service landing under `src/myproj/core/governance`
- compatibility re-exports from `src/policy_control`

Acceptance:

- `src/myproj` can own delegation decisions
- `src/policy_control` can be reduced to adapters/shims

Dependencies:

- B002

### B021. Move approval services into `src/myproj`

Deliver:

- approval models/services/state handling under `src/myproj/core/approvals`

Acceptance:

- approval behavior can be invoked from core services without crossing package boundaries awkwardly

Dependencies:

- B002

### B022. Move risk and policy orchestration into `src/myproj`

Deliver:

- risk synthesis and policy evaluation under core package

Acceptance:

- thread runtime can compute policy/risk outcomes without external module indirection

Dependencies:

- B002

### B023. Introduce authority-aware approval payloads

Deliver:

- approval requests contain sender stack, disclosure preview, and action envelope reference

Acceptance:

- approval UI and APIs can show structured authority information

Dependencies:

- B001
- B021

## Phase 4: Core <-> E3 Integration

Purpose:

- replace ad hoc action execution with a formal action fabric contract

P0 backlog:

### B030. Define `ActionEnvelope`

Deliver:

- a stable shared contract carrying thread context, sender stack, risk posture, and execution intent

Acceptance:

- E3 can consume the envelope without route-specific custom parsing

Dependencies:

- B001

### B031. Update E3 API and engine to use shared action contracts

Deliver:

- E3 endpoints and runtime aligned to `ActionEnvelope`

Acceptance:

- E3 tests still pass
- action creation and execution paths remain idempotent

Dependencies:

- B030

### B032. Feed execution results back into core replay

Deliver:

- execution outcomes become first-class events in the core replay chain

Acceptance:

- thread replay shows draft, approval, execution, delivery, and acknowledgement milestones

Dependencies:

- B031
- B003

## Phase 5: Operator Console Upgrade

Purpose:

- reflect the real product model in the UI

P0 backlog:

### B040. Upgrade thread detail page into thread workspace

Deliver:

- thread objective
- delegation summary
- next action preview
- replay panel
- approval and control affordances

Acceptance:

- thread detail no longer reads like a generic chat transcript

Dependencies:

- B023
- B032

### B041. Upgrade approval inbox

Deliver:

- sender stack preview
- action preview
- risk explanation
- approve/modify/reject/take-over controls

Acceptance:

- approval objects are intelligible without leaving the screen

Dependencies:

- B023

### B042. Upgrade replay center

Deliver:

- replay grouped by decision chain stages
- authority and disclosure visibility
- execution milestones

Acceptance:

- replay communicates responsibility, not just chronology

Dependencies:

- B003
- B032

### B043. Add relationship and authority management screens

Deliver:

- relationship policy presets
- authority grant configuration
- disclosure defaults

Acceptance:

- users can configure who may represent them and under what boundaries

Dependencies:

- B001
- B020

## Phase 6: Hardening And End-to-End Validation

Purpose:

- prove the kernel is coherent

P0 backlog:

### B050. Add end-to-end thread/action/replay integration tests

Acceptance:

- thread -> approval -> execution -> replay works in one integrated flow

### B051. Add migration/build/packaging CI checks

Acceptance:

- CI verifies package install, web build, and basic migration health

### B052. Produce scenario demos

Acceptance:

- interview scheduling
- customer/vendor follow-up
- approval-gated outbound message

## 5. Prioritization

### P0: Must land before broader product expansion

- B001
- B003
- B010
- B011
- B012
- B020
- B021
- B022
- B023
- B030
- B031
- B032
- B040
- B041
- B042

### P1: Very important, can trail slightly if needed

- B043
- B050
- B051
- B052

### P2: Later optimization

- federation
- org-to-org authority exchange
- richer interrupt policies
- transport expansion

## 6. Suggested Delivery Sequence

Week 1:

- contract freeze
- contracts package
- governance landing zones
- repository plan locked

Week 2:

- repository implementations
- DB mappings
- governance migration scaffolding
- E3 action contract adaptation begins

Week 3:

- route migration
- authority-aware approval payloads
- E3 contract integration
- replay payload enrichment

Week 4:

- operator console uplift
- end-to-end tests
- integration hardening

## 7. Main Execution Risks

### Risk 1: Too many teams edit the same files

Mitigation:

- freeze write scopes before coding
- use a lead integrator for shared exports and final wiring

### Risk 2: Product contracts remain ambiguous

Mitigation:

- no parallel coding starts until sender stack and authority semantics are frozen

### Risk 3: Governance merge becomes a rename exercise

Mitigation:

- move behavior and interfaces first
- rename packages only after behavior stabilizes

### Risk 4: Frontend outpaces backend semantics

Mitigation:

- agree on API contract examples early
- front-end team can prototype against typed mock payloads that mirror frozen contracts

## 8. Summary

The next phase is not about adding more AI features.
It is about turning the repository into a stable communication kernel where identity, delegation, approval, replay, and execution fit together as one product.
