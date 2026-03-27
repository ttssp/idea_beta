# Contract Design Decisions

## Purpose
This document records the key design decisions for the Communication OS shared contracts package. These decisions are frozen for Phase 0 and should not be modified without Lead approval.

## Decision Log

### 1. Contract Base Class: `ContractModel`
**Date**: 2026-03-27
**Decision**: Use Pydantic BaseModel with `extra="forbid"`
**Rationale**:
- Strict validation prevents accidental field additions
- Ensures contract stability across layers
- `extra="forbid"` catches typos and mismatches early
**Implications**: All fields must be explicitly declared; no dynamic extensions

---

### 2. UUID Field Naming Convention
**Date**: 2026-03-27
**Decision**: Use `*_id` for single UUIDs, `*_ids` for lists
**Rationale**:
- Consistent with product spec vocabulary
- Clear distinction between single and multiple
- Easy to grep and refactor
**Examples**:
- `owner_id`, `thread_id` (single)
- `participant_ids`, `relationship_ids` (list)

---

### 3. Sender Stack Fields: Owner/Delegate/Author/Approver/Executor
**Date**: 2026-03-27
**Decision**: Exact five-role model from spec section 9.2
**Rationale**:
- Directly maps to product spec requirements
- Covers all delegation scenarios in v1
- No synonyms allowed to prevent confusion
**Role Definitions**:
- `owner`: Ultimately represented human/organization
- `delegate`: Agent acting on behalf at runtime
- `author`: Who drafted content/prepared payload
- `approver`: Who explicitly approved (if any)
- `executor`: System/service that delivered/enacted

---

### 4. Disclosure Mode Enumeration
**Date**: 2026-03-27
**Decision**: Four modes: FULL, SEMI, TEMPLATE, HIDDEN
**Rationale**:
- Matches spec section 10.1 exactly
- Covers all disclosure needs for v1 scenarios
- HIDDEN is restricted to internal low-risk only
**Rules**:
- External requires at least SEMI
- High-risk requires FULL
- Sensitive relationships require FULL

---

### 5. Delegation Mode Levels
**Date**: 2026-03-27
**Decision**: Five levels: OBSERVE_ONLY, DRAFT_FIRST, APPROVE_TO_SEND, BOUNDED_AUTO, HUMAN_ONLY
**Rationale**:
- From spec section 11.1
- Progressive authority from read-only to fully delegated
- Clear escalation path through levels
**Order of increasing authority**:
1. OBSERVE_ONLY (read-only)
2. DRAFT_FIRST (prepare, no send)
3. APPROVE_TO_SEND (prepare + approval gate)
4. BOUNDED_AUTO (auto-execute within bounds)
5. HUMAN_ONLY (no delegation allowed)

---

### 6. Principal Kind vs Principal Type
**Date**: 2026-03-27
**Decision**: Keep separate enums for contracts vs domain
**Rationale**:
- `PrincipalKind` (contracts): Richer, product-facing types
- `PrincipalType` (domain): Simpler, storage-focused types
- Clear separation of concerns
- Contracts layer can evolve independently
**Mapping**:
```
PrincipalKind.HUMAN → PrincipalType.HUMAN
PrincipalKind.PERSONAL_AGENT → PrincipalType.AGENT
PrincipalKind.ORGANIZATION_AGENT → PrincipalType.AGENT
PrincipalKind.SERVICE_AGENT → PrincipalType.SERVICE
PrincipalKind.EXTERNAL_PARTICIPANT → PrincipalType.EXTERNAL
PrincipalKind.PUBLIC_SERVICE_AGENT → PrincipalType.SERVICE
```

---

### 7. Risk Level Four-Tier Model
**Date**: 2026-03-27
**Decision**: LOW, MEDIUM, HIGH, CRITICAL with numeric ordering
**Rationale**:
- Four tiers provide enough granularity
- Numeric ordering enables comparison
- CRITICAL requires FULL disclosure
- LOW allows auto-execution with proper bounds
**Order**: LOW (0) < MEDIUM (1) < HIGH (2) < CRITICAL (3)

---

### 8. Action Envelope as Shared Contract
**Date**: 2026-03-27
**Decision**: ActionEnvelope carries all context from core → E3 → UI
**Rationale**:
- Single source of truth for action intent
- Contains thread context, sender stack, disclosure preview, risk posture
- Enables idempotency via idempotency_key
- Allows execution_mode to control behavior
**Key Fields**:
- `thread`: ThreadContextRef
- `sender_stack`: SenderStack
- `disclosure_preview`: DisclosurePreview
- `risk_posture`: RiskPosture
- `target`: ActionTarget
- `execution_mode`: ActionExecutionMode

---

### 9. Serialization Strategy
**Date**: 2026-03-27
**Decision**: Pydantic model_dump(mode="json") for all contract serialization
**Rationale**:
- Consistent serialization across layers
- UUIDs converted to strings automatically
- datetime handled properly
- Example payloads use this format
**Rule**: Never use pickle or custom serialization for contracts

---

### 10. Example Payloads as Living Documentation
**Date**: 2026-03-27
**Decision**: Maintain example objects + JSON payloads in examples.py
**Rationale**:
- Examples serve as documentation
- Round-trip tests verify examples work
- Frontend/E3 teams can copy-paste for mocks
- Three scenario examples included:
  - Interview scheduling
  - Customer follow-up
  - Approval-gated external communication

---

## Frozen Contracts (Do Not Modify)

These contracts are frozen for Phase 0:
- `AuthorityGrant`
- `SenderStack`
- `DisclosurePolicy` / `DisclosurePreview`
- `AttentionDecision`
- `ActionEnvelope`
- All supporting types and enums

## Change Request Process

To modify a frozen contract:
1. Write a detailed proposal explaining the change and why it's necessary
2. Show impact analysis on all layers (core, E3, UI, E5)
3. Get Lead approval
4. Update all related tests and examples
5. Update this document with the new decision

## Imports

Contracts should be imported from:
```python
from myproj.core.contracts import (
    AuthorityGrant,
    SenderStack,
    DisclosurePolicy,
    ActionEnvelope,
    AttentionDecision,
    # ... etc
)
```

Never import from individual contract modules directly - use the package export.
