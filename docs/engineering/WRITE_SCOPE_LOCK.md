# Write Scope Lock

## Purpose
This document defines write scope ownership for the Parallel Engineering phase. **DO NOT MODIFY FILES OUTSIDE YOUR ASSIGNED SCOPE WITHOUT LEAD APPROVAL.**

## Shared Files (Lead Only)

These files may only be modified by the Lead Integrator:

| Path | Reason |
|------|--------|
| `src/myproj/core/contracts/**/*.py` | Frozen contracts - stability critical |
| `src/myproj/core/contracts/__init__.py` | Export surface - stability critical |
| `src/myproj/infra/db/models.py` | Shared DB schema - coordination required |
| `docs/product/**/*.md` | Product specs - single source of truth |
| `docs/engineering/**/*.md` | Engineering plans - single source of truth |

**Exception**: Engineers may add comments/docs to these files with Lead approval.

---

## Engineer Write Scopes

### Engineer 1: Core Contracts Engineer (Completed)
**Owned Scope**:
- `src/myproj/core/contracts/**` - *FROZEN after Sprint 0*
- `tests/unit/contracts/**`

**Delivered**:
- AuthorityGrant, SenderStack, DisclosurePolicy, AttentionDecision, ActionEnvelope contracts
- Complete test coverage
- Example payloads and handoff docs

---

### Engineer 2: Core Persistence And API Engineer
**Owned Scope**:
- `src/myproj/core/repositories/**`
- `src/myproj/infra/db/models.py` (only with Lead approval)
- `src/myproj/api/v1/messages.py`
- `src/myproj/api/v1/principals.py`
- `src/myproj/api/v1/relationships.py`
- `src/myproj/api/v1/events.py`
- `tests/conftest.py`
- `tests/unit/test_api_endpoints.py`

**Forbidden**:
- Do NOT modify `src/policy_control/**`
- Do NOT modify `backend/e3/**`
- Do NOT modify frontend code
- Do NOT modify contracts without Lead approval

---

### Engineer 3: Governance Kernel Engineer
**Owned Scope**:
- `src/myproj/core/governance/**`
- `src/myproj/core/approvals/**`
- `src/myproj/core/risk/**`
- `src/policy_control/**` (may modify, but prefer moving to myproj)

**Migration Strategy**:
1. Create new landing zones under `src/myproj/core/*/`
2. Move implementation gradually from `src/policy_control/`
3. Leave re-export shims in `src/policy_control/` for compatibility
4. Align types with frozen contracts

**Forbidden**:
- Do NOT modify `src/myproj/api/v1/**` without Lead approval
- Do NOT modify `backend/e3/**`
- Do NOT modify frontend code
- Do NOT modify contracts without Lead approval

---

### Engineer 4: Execution Fabric Engineer
**Owned Scope**:
- `backend/e3/**`
- `backend/e3/tests/**`

**Integration Points**:
- Consume `ActionEnvelope` from frozen contracts
- Emit events that map to core replay events
- Preserve idempotency and delivery guarantees
- Use contracts from `myproj.core.contracts` (do NOT duplicate types)

**Forbidden**:
- Do NOT modify `src/myproj/api/v1/**` without Lead approval
- Do NOT modify `src/policy_control/**`
- Do NOT modify frontend code
- Do NOT modify contracts without Lead approval

---

### Engineer 5: Frontend Operator Console Engineer
**Owned Scope**:
- `src/app/(app)/threads/**`
- `src/app/(app)/approvals/**`
- `src/app/(app)/replay/**`
- `src/app/(app)/settings/**`
- `src/components/approval/**`
- `src/components/replay/**`
- `src/components/thread/**`
- `src/lib/types/**`
- `src/lib/api/**`

**Mock Strategy**:
- Use JSON fixtures from `tests/fixtures/contracts/` for mocks
- Reference `examples.py` for payload structures
- Can prototype against frozen examples before backend integration

**Forbidden**:
- Do NOT modify `backend/e3/**`
- Do NOT modify `src/policy_control/**`
- Do NOT modify repository and DB files
- Do NOT modify contracts without Lead approval

---

### Optional Engineer 6: Intelligence Layer Engineer
**Owned Scope**:
- `src/e5/**`
- Web tests exercising E5-facing flows

**Alignment**:
- Emit structured action recommendations aligned to `ActionEnvelope`
- Include explanation artifacts suitable for replay
- Attach confidence and escalation metadata

**Forbidden**:
- Do NOT modify `backend/e3/**` without Lead approval
- Do NOT modify governance merge files without Lead approval
- Do NOT modify contracts without Lead approval

---

## Cross-Scope Changes

### When You Need to Modify Another Engineer's Scope

1. **Talk to the owner first** - discuss the change needed
2. **If agreement reached**:
   - Owner makes the change, or
   - Owner gives explicit permission for you to make the change
3. **If no agreement or urgent**:
   - Escalate to Lead
   - Lead decides and coordinates

### When You Need to Modify Shared Files

1. **Create a proposal** - explain what needs to change and why
2. **Submit to Lead** - via PR, Slack, or meeting
3. **Wait for approval** - Lead will review and either:
   - Approve and make the change
   - Approve and let you make the change
   - Request modifications
   - Reject with explanation

---

## Branch Strategy

### Branch Naming Convention
```
feature/{engineer-role}/{description}
```

Examples:
- `feature/eng2/repository-impl`
- `feature/eng3/governance-landing-zones`
- `feature/eng4/e3-action-contract`
- `feature/eng5/thread-workspace`

### Integration Branch
- **Name**: `feature/contract-integration`
- **Owner**: Lead
- **Purpose**: Final integration point before main
- **Rule**: Only Lead merges to this branch

### Merge Order
1. Engineer 1 contracts (already done)
2. Engineer 3 governance landing zones
3. Engineer 2 repositories and API migration
4. Engineer 4 E3 action contract changes
5. Engineer 5 frontend integration
6. Optional Engineer 6 E5 integration
7. Lead final integration

---

## PR Review Requirements

### PRs to Owned Scopes
- 1 approval from team member sufficient
- Can merge when ready (after approval)

### PRs Touching Multiple Scopes
- Must have approval from each affected engineer
- Lead review recommended

### PRs Touching Shared Files
- **Requires Lead approval ONLY**
- No other approvals needed but Lead may request them

---

## Conflict Resolution

### Code Conflicts
1. Try to resolve with the other engineer first
2. If unable, escalate to Lead
3. Lead makes final decision

### Design Disagreements
1. Document both approaches with pros/cons
2. Discuss in team sync
3. Lead makes final decision if no consensus

---

## Emergency Hotfixes

If something is blocking progress urgently:

1. Message Lead immediately
2. If Lead unavailable and critically blocked:
   - Make the minimal necessary change
   - Add a comment: `// HOTFIX: [your name] - [reason] - [date]`
   - Notify Lead as soon as possible
   - Lead will review and either keep, modify, or revert

**Use this sparingly** - prefer waiting for Lead when possible.

---

## Contact

Questions about scope? Reach out to the Lead Integrator.

Last updated: 2026-03-27
