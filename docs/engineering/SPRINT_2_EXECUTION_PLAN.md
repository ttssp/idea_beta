# Sprint 2: Final Integration Plan

**Status**: 📋 Planning
**Start Date**: TBD
**Duration**: 3-5 days
**Owner**: Lead / Integrator

---

## Overview

Sprint 2 is the final integration phase where all parallel workstreams from Sprint 1 come together into a single coherent Communication OS kernel.

### Objectives
- ✅ Integrate all Sprint 1 deliverables
- ✅ Resolve schema mismatches across packages
- ✅ Build end-to-end thread/action/approval/replay flows
- ✅ Polish the replay and approval user experience
- ✅ Validate the complete Communication OS story

---

## Phase 0: Pre-Integration Assessment (0.5 days)

### Goals
- Assess current state of all Sprint 1 branches
- Identify integration conflicts early
- Create integration branch strategy

### Tasks

#### T0.1 - Current State Inventory
**Owner**: Lead
- [ ] Review all completed Sprint 1 deliverables
- [ ] List all modified files and packages
- [ ] Identify potential schema mismatches
- [ ] Document API contract differences

**Deliverable**: Integration Assessment Report

#### T0.2 - Integration Branch Setup
**Owner**: Lead
- [ ] Create `feature/sprint2-integration` branch from main
- [ ] Set up branch protection rules
- [ ] Configure CI/CD for integration testing
- [ ] Create integration test skeleton

**Key Files**:
- New integration branch: `feature/sprint2-integration`
- New test directory: `tests/integration/`

---

## Phase 1: Core Integration (1 day)

### Goals
- Merge all backend packages
- Resolve type and schema conflicts
- Establish unified API surface

### Tasks

#### T1.1 - Contract & Governance Integration
**Owner**: Lead
- [ ] Verify contracts package exports are complete
- [ ] Integrate governance landing zones with core
- [ ] Ensure policy_control compatibility layer works
- [ ] Run all governance and contract tests

**Key Files**:
- `src/myproj/core/contracts/__init__.py`
- `src/myproj/core/governance/__init__.py`
- `src/myproj/core/approvals/__init__.py`
- `src/myproj/core/risk/__init__.py`
- `src/policy_control/__init__.py`

**Acceptance**: All 11 governance tests pass

#### T1.2 - Repository Integration
**Owner**: Lead
- [ ] Verify all repositories are properly exported
- [ ] Test repository initialization and dependency injection
- [ ] Ensure repository pattern consistency across all implementations
- [ ] Run all repository tests

**Key Files**:
- `src/myproj/core/repositories/__init__.py`
- `src/myproj/core/repositories/thread_repository.py`
- `src/myproj/core/repositories/message_repository.py`
- `src/myproj/core/repositories/principal_repository.py`
- `src/myproj/core/repositories/relationship_repository.py`
- `src/myproj/core/repositories/event_repository.py`

**Acceptance**: All 13 repository tests pass

#### T1.3 - Schema Conflict Resolution
**Owner**: Lead
- [ ] Check for enum value consistency across packages
- [ ] Verify UUID field naming conventions
- [ ] Resolve any duplicate type definitions
- [ ] Ensure JSON serialization compatibility

**Key Areas**:
- RiskLevel enum consistency
- DisclosureMode enum consistency
- PrincipalType/PrincipalKind alignment
- Timestamp format standardization

**Deliverable**: Schema Alignment Checklist

---

## Phase 2: E3 & Execution Fabric Integration (1 day)

### Goals
- Connect core with E3 execution fabric
- Ensure ActionEnvelope flows end-to-end
- Establish replay event pipeline

### Tasks

#### T2.1 - ActionEnvelope Flow Integration
**Owner**: Lead
- [ ] Verify E3 contract adapter works with core
- [ ] Test ActionEnvelope validation in E3
- [ ] Ensure sender stack propagation through E3
- [ ] Test disclosure preview handling

**Key Files**:
- `backend/e3/action_runtime/contract_adapter.py`
- `backend/e3/api/v1/actions.py`
- `src/myproj/core/contracts/actions.py`

**Acceptance**: All 15 E3 ActionEnvelope tests pass

#### T2.2 - Replay Event Pipeline
**Owner**: Lead
- [ ] Create replay event emitter interface
- [ ] Connect E3 execution results to core event store
- [ ] Ensure event schema compatibility for replay
- [ ] Test event round-trip serialization

**Key Components**:
- ExecutionResultEmitter (E3)
- EventRepository (core)
- ThreadEvent domain model

**Deliverable**: Replay Event Flow Diagram

#### T2.3 - Idempotency & Delivery Guarantees
**Owner**: Lead
- [ ] Verify idempotency key flow end-to-end
- [ ] Test delivery status tracking
- [ ] Ensure at-least-once delivery semantics
- [ ] Validate duplicate action prevention

**Key Files**:
- `backend/e3/core/idempotency.py`
- `src/myproj/core/domain/event.py`

---

## Phase 3: Frontend & API Integration (1 day)

### Goals
- Connect frontend with integrated backend
- Polish approval and replay UI
- Ensure type safety across stack

### Tasks

#### T3.1 - API Contract Validation
**Owner**: Lead + Engineer 5
- [ ] Verify TypeScript types match Python contracts
- [ ] Test API endpoint integration
- [ ] Ensure JSON fixtures work with frontend
- [ ] Validate error handling and loading states

**Key Files**:
- `src/lib/types/contracts.ts`
- `src/lib/api/*.ts`
- `tests/fixtures/contracts/*.json`

**Acceptance**: Frontend typecheck passes with no errors

#### T3.2 - Approval Experience Polish
**Owner**: Lead + Engineer 5
- [ ] Enhance approval card with sender stack display
- [ ] Add disclosure preview to approval detail
- [ ] Show risk posture and reasoning
- [ ] Test approval action flows

**Key Components**:
- `src/components/approval/ApprovalCard.tsx`
- `src/components/approval/ApprovalPreview.tsx`
- `src/app/(app)/approvals/page.tsx`
- `src/app/(app)/approvals/[id]/page.tsx`

**Acceptance**: Approval UI clearly shows authority chain

#### T3.3 - Replay Timeline Enhancement
**Owner**: Lead + Engineer 5
- [ ] Enhance replay timeline with responsibility stages
- [ ] Add sender stack tooltip to replay events
- [ ] Show disclosure mode indicators
- [ ] Test full thread replay flow

**Key Components**:
- `src/components/replay/ReplayTimeline.tsx`
- `src/app/(app)/replay/page.tsx`
- `src/app/(app)/replay/[id]/page.tsx`

**Acceptance**: Replay tells authority story, not just chronology

#### T3.4 - Thread Workspace Integration
**Owner**: Lead + Engineer 5
- [ ] Integrate thread header with delegation info
- [ ] Connect thread timeline with event repository
- [ ] Add action preview panel
- [ ] Test full thread workspace experience

**Key Components**:
- `src/components/thread/ThreadHeader.tsx`
- `src/components/thread/ThreadTimeline.tsx`
- `src/components/thread/ThreadActionBar.tsx`
- `src/app/(app)/threads/[id]/page.tsx`

**Acceptance**: Thread detail reads as a workspace, not a chat transcript

---

## Phase 4: End-to-End Testing & Hardening (0.5-1 days)

### Goals
- Build comprehensive end-to-end tests
- Validate the complete Communication OS story
- Polish edge cases and error handling

### Tasks

#### T4.1 - End-to-End Test Framework
**Owner**: Lead
- [ ] Create end-to-end test infrastructure
- [ ] Set up test database and fixtures
- [ ] Create test data generators
- [ ] Establish clean test isolation

**Key Files**:
- `tests/integration/conftest.py`
- `tests/integration/fixtures.py`
- `tests/integration/test_e2e_flow.py`

#### T4.2 - Core Flow E2E Tests
**Owner**: Lead
- [ ] Test: Create thread → prepare action → get approval decision
- [ ] Test: Approve action → execute via E3 → see delivery status
- [ ] Test: Replay full thread with authority visibility
- [ ] Test: Delegation scenario with full sender stack

**Scenarios**:
1. Interview scheduling flow
2. Customer follow-up flow
3. Approval-gated external communication

**Acceptance**: All E2E scenarios pass

#### T4.3 - Edge Case Hardening
**Owner**: Lead
- [ ] Test concurrent action execution
- [ ] Test network failure recovery
- [ ] Test idempotency with duplicate requests
- [ ] Test large thread replay performance
- [ ] Test error boundary handling in UI

#### T4.4 - Final Demo Preparation
**Owner**: Lead
- [ ] Create demo script for complete flow
- [ ] Set up demo data and environment
- [ ] Record walkthrough video (optional)
- [ ] Prepare acceptance checklist

**Deliverable**: Sprint 2 Acceptance Demo

---

## Integration Sequence

### Merge Order (Critical!)
Following PARALLEL_ENGINEERING_PLANS.md Section 7:

1. **Engineer 1 contracts** (already in main)
2. **Engineer 3 governance landing zones** ✓ (completed)
3. **Engineer 2 repositories and API migration** ✓ (completed)
4. **Engineer 4 E3 action contract changes** ✓ (completed)
5. **Engineer 5 frontend integration** ✓ (completed)
6. **Optional Engineer 6 E5 integration** (if available)
7. **Lead final integration branch** 🚧 (current phase)

### Integration Strategy
- Use **merge commits** for traceability
- Run **full test suite** after each merge
- Create **fix commits** for integration issues
- Tag **integration checkpoints** after each phase

---

## Acceptance Criteria

### Sprint 2 Complete When:

#### Technical Criteria
- [ ] All 159+ unit tests pass
- [ ] All E2E scenarios pass
- [ ] No schema mismatches across packages
- [ ] TypeScript and Python types are aligned
- [ ] CI/CD pipeline is green

#### Product Criteria
- [ ] One coherent end-to-end story works:
  1. User opens a thread
  2. System determines relationship and delegation context
  3. Action is prepared with legible sender stack
  4. Policy and risk decide auto-run/approval/escalate
  5. Action executes through E3
  6. Full chain is replayable in UI
- [ ] Approval previews show sender stack and disclosure
- [ ] Replay shows responsibility stages, not just chronology
- [ ] Thread detail is a workspace, not a chat transcript

#### Documentation Criteria
- [ ] Integration Assessment Report
- [ ] Schema Alignment Checklist
- [ ] Replay Event Flow Diagram
- [ ] Sprint 2 Acceptance Demo

---

## Risk Mitigation

### Risk 1: Integration conflicts cause regressions
**Mitigation**:
- Run full test suite after each merge
- Use feature flags for incomplete features
- Maintain rollback points at each phase

### Risk 2: Schema mismatches break API
**Mitigation**:
- Create schema validation tests
- Use Pydantic models for all API boundaries
- Maintain JSON schema fixtures for contract testing

### Risk 3: E2E tests are flaky
**Mitigation**:
- Use proper test isolation
- Create deterministic test data
- Add retries for timing-sensitive tests
- Separate fast unit tests from slow E2E tests

---

## Timeline Summary

| Phase | Duration | Main Activities |
|-------|----------|-----------------|
| Phase 0 | 0.5 days | Pre-integration assessment |
| Phase 1 | 1 day | Core integration (contracts, governance, repos) |
| Phase 2 | 1 day | E3 & execution fabric integration |
| Phase 3 | 1 day | Frontend & API integration |
| Phase 4 | 0.5-1 days | E2E testing & hardening |
| **Total** | **4-5 days** | **Sprint 2 Complete** |

---

## Key Deliverables

### Documents
- `docs/engineering/INTEGRATION_ASSESSMENT.md`
- `docs/engineering/SCHEMA_ALIGNMENT_CHECKLIST.md`
- `docs/engineering/REPLAY_EVENT_FLOW.md`

### Code
- `tests/integration/test_e2e_flow.py`
- `tests/integration/conftest.py`
- Integration fixes as needed

### Demo
- Sprint 2 Acceptance Demo script
- Demo environment setup
- Walkthrough video (optional)

---

## Post-Sprint 2: Next Steps

After Sprint 2 completion:
1. **Demo to stakeholders** - Show the complete Communication OS
2. **Collect feedback** - Gather input on UX and functionality
3. **Plan Sprint 3** - Focus on polishing, performance, and additional features
4. **Prepare for production** - Hardening, monitoring, and deployment

---

## Communication Plan

### Daily Standups
- **Time**: Morning (15 min)
- **Focus**: Blockers, progress, integration issues
- **Attendees**: All engineers who worked on Sprint 1

### Integration Checkpoints
- After Phase 1: Core integration review
- After Phase 2: E3 integration review
- After Phase 3: Frontend integration review
- After Phase 4: Final acceptance review

### Demo
- **End of Sprint 2**: Full acceptance demo
- **Attendees**: All stakeholders
- **Format**: Live demo + walkthrough
