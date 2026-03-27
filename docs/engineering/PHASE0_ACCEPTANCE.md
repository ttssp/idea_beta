# Phase 0 Acceptance Checklist

## Sprint 0 Exit Criteria

This document defines the acceptance criteria for Phase 0 (Contract Freeze).

---

## 1. Contract Completeness

- [x] `AuthorityGrant` implements all spec section 8.2 required fields
- [x] `SenderStack` includes owner/delegate/author/approver/executor from spec section 9.2
- [x] `DisclosurePolicy` implements 4 modes: FULL, SEMI, TEMPLATE, HIDDEN
- [x] `AttentionDecision` covers all spec section 8.9 output types
- [x] `ActionEnvelope` carries thread, sender stack, disclosure, risk, and target

---

## 2. Contract Consistency

- [x] All UUID fields use `*_id` / `*_ids` naming convention
- [x] No conflicting enum definitions across contract modules
- [x] All models inherit from `ContractModel` with `extra="forbid"`
- [x] Shared types imported from `myproj.core.contracts` package

---

## 3. Test Coverage

- [x] Unit tests for all contract models exist
- [x] All invariants and validators have corresponding tests
- [x] Serialization/deserialization round-trip tests pass
- [x] Example payload round-trip tests pass
- [x] Edge cases and error paths tested

---

## 4. Documentation

- [x] `CONTRACT_DESIGN_DECISIONS.md` created with 10+ key decisions
- [x] `CONTRACT_FIELD_REFERENCE.md` created with all fields documented
- [x] `WRITE_SCOPE_LOCK.md` defines clear ownership boundaries
- [x] This document (`PHASE0_ACCEPTANCE.md`) created
- [x] Inline docstrings for all public methods and classes

---

## 5. Example Payloads

- [x] `examples.py` includes `AUTHORITY_GRANT_EXAMPLE`
- [x] `examples.py` includes `SENDER_STACK_EXAMPLE`
- [x] `examples.py` includes `DISCLOSURE_POLICY_EXAMPLE` + `DISCLOSURE_PREVIEW_EXAMPLE`
- [x] `examples.py` includes `ATTENTION_DECISION_EXAMPLE`
- [x] `examples.py` includes `ACTION_ENVELOPE_EXAMPLE`
- [x] All examples export JSON payloads via `model_dump(mode="json")`
- [x] JSON fixtures created in `tests/fixtures/contracts/`

---

## 6. TypeScript Types

- [x] `src/lib/types/contracts.ts` created with all contract types
- [x] Types generated from Pydantic models (or manually aligned)
- [x] Enum values match Python exactly
- [x] Optional fields correctly marked as optional

---

## 7. Integration Prep

- [x] `tests/integration/test_contract_flow.py` skeleton created
- [x] End-to-end flow documented: thread → approval → execution → replay
- [x] Test data generator patterns established
- [x] Merge order defined in `WRITE_SCOPE_LOCK.md`

---

## Engineer Deliverable Acceptance

### Engineer 2 Acceptance
- [ ] Can import all needed types from `myproj.core.contracts`
- [ ] Has clear write scope in `WRITE_SCOPE_LOCK.md`
- [ ] Has JSON fixtures for repository testing
- [ ] Understands contract stability guarantees

### Engineer 3 Acceptance
- [ ] Can import all needed types from `myproj.core.contracts`
- [ ] Has clear write scope in `WRITE_SCOPE_LOCK.md`
- [ ] Understands governance landing zone structure
- [ ] Understands compatibility shim strategy

### Engineer 4 Acceptance
- [ ] Can import `ActionEnvelope` and related types
- [ ] Has clear write scope in `WRITE_SCOPE_LOCK.md`
- [ ] Has JSON fixtures for E3 testing
- [ ] Understands idempotency requirements

### Engineer 5 Acceptance
- [ ] Has TypeScript types in `src/lib/types/contracts.ts`
- [ ] Has clear write scope in `WRITE_SCOPE_LOCK.md`
- [ ] Has JSON fixtures for frontend mocks
- [ ] Understands UI/backend contract alignment

---

## Final Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Lead | | | |
| Engineer 1 | | | |
| Engineer 2 | | | |
| Engineer 3 | | | |
| Engineer 4 | | | |
| Engineer 5 | | | |

---

## Post-Acceptance

Once this checklist is signed off:

1. ✅ Contracts are FROZEN - no changes without Lead approval
2. ✅ Sprint 1 can begin with parallel engineering
3. ✅ All engineers work in their assigned write scopes
4. ✅ Lead coordinates integration and conflict resolution

## Known Limitations & Future Work

- Federation and multi-org semantics deferred to later phase
- Richer interrupt policies deferred to later phase
- Transport expansion deferred to later phase
