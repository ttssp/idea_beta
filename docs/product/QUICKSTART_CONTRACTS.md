# Contracts Quick Start Guide

## Getting Started in 5 Minutes

This guide helps all engineers start using the frozen contracts immediately.

---

## For All Engineers

### 1. Import from the Right Place

```python
# GOOD - Always import from the package
from myproj.core.contracts import (
    AuthorityGrant,
    SenderStack,
    DisclosurePolicy,
    ActionEnvelope,
    AttentionDecision,
    RiskLevel,
    DisclosureMode,
    ActorRef,
)

# BAD - Don't import from individual modules
from myproj.core.contracts.authority import AuthorityGrant
```

### 2. Use the Examples for Reference

```python
from myproj.core.contracts.examples import (
    AUTHORITY_GRANT_EXAMPLE,
    SENDER_STACK_EXAMPLE,
    ACTION_ENVELOPE_EXAMPLE,
    # JSON payloads:
    AUTHORITY_GRANT_PAYLOAD,
    ACTION_ENVELOPE_PAYLOAD,
)

# Copy-paste and modify
my_stack = SENDER_STACK_EXAMPLE.model_copy(
    update={"authority_label": "my_policy_v2"}
)
```

### 3. Load JSON Fixtures for Mocks

```python
import json
from pathlib import Path

FIXTURE_DIR = Path("tests/fixtures/contracts")

# Load action envelope for frontend/E3 mocks
with open(FIXTURE_DIR / "action_envelope.json") as f:
    envelope_data = json.load(f)
```

---

## For Engineer 2 (Persistence & API)

### Repository Pattern with Contracts

```python
from myproj.core.contracts import AuthorityGrant
from myproj.core.repositories import BaseRepository

class AuthorityGrantRepository(BaseRepository[AuthorityGrant]):
    model_class = AuthorityGrant

    async def get_active_for_delegate(
        self,
        delegate_id: UUID
    ) -> list[AuthorityGrant]:
        return [
            grant async for grant in self.all()
            if grant.delegate.principal_id == delegate_id
            and grant.is_currently_active
        ]
```

### Key Files to Reference
- `CONTRACT_FIELD_REFERENCE.md` - All field definitions
- `tests/fixtures/contracts/*.json` - Example payloads
- `tests/integration/test_contract_flow.py` - Usage patterns

---

## For Engineer 3 (Governance Kernel)

### Align with Frozen Contracts

```python
# When moving code from policy_control to myproj:
from myproj.core.contracts import (
    DelegationMode,  # Use this, NOT the old enum
    RiskLevel,       # Use this, NOT the old enum
    DisclosureMode,  # Use this, NOT the old enum
)

# Create compatibility shims in policy_control:
from myproj.core.governance import DelegationService
# Re-export for backward compatibility
__all__ = ["DelegationService"]
```

### Landing Zones to Create
- `src/myproj/core/governance/`
- `src/myproj/core/approvals/`
- `src/myproj/core/risk/`

---

## For Engineer 4 (Execution Fabric)

### Consume ActionEnvelope

```python
from myproj.core.contracts import (
    ActionEnvelope,
    ActionExecutionMode,
    SenderStack,
)

async def execute_action(envelope: ActionEnvelope) -> dict:
    # Validate envelope
    if envelope.execution_mode == ActionExecutionMode.PREPARE_ONLY:
        return {"status": "prepared", "envelope_id": envelope.envelope_id}

    # Use sender stack for audit
    stack = envelope.sender_stack
    print(f"Executing on behalf of {stack.owner.display_name}")

    # Execute through channel adapter
    result = await channel_adapter.send(envelope)

    # Emit event back to core for replay
    await emit_execution_event(envelope, result)
    return result
```

### JSON Fixtures for Testing
```python
# Use the fixture directly in E3 tests
import json
with open("tests/fixtures/contracts/action_envelope.json") as f:
    data = json.load(f)
    envelope = ActionEnvelope.model_validate(data)
```

---

## For Engineer 5 (Frontend)

### Use TypeScript Types

```typescript
import {
  ActionEnvelope,
  SenderStack,
  DisclosurePreview,
  AttentionDecision,
  AttentionDisposition,
  RiskLevel,
} from '@/lib/types/contracts';

// Type-safe component
interface ApprovalCardProps {
  envelope: ActionEnvelope;
  onApprove: () => void;
  onReject: () => void;
}

export function ApprovalCard({ envelope, onApprove, onReject }: ApprovalCardProps) {
  const { sender_stack, disclosure_preview, risk_posture } = envelope;

  return (
    <div>
      <h3>{envelope.action_label}</h3>
      <SenderStackView stack={sender_stack} />
      <DisclosureView preview={disclosure_preview} />
      <RiskBadge level={risk_posture.risk_level} />
      {/* ... */}
    </div>
  );
}
```

### Load JSON Fixtures for Mocks

```typescript
// In your test files or mock data
import actionEnvelopeFixture from '@/../tests/fixtures/contracts/action_envelope.json';
import { ActionEnvelope } from '@/lib/types/contracts';

const mockEnvelope = actionEnvelopeFixture as ActionEnvelope;
```

### Key Types to Use
- `ActionEnvelope` - Main action payload
- `SenderStack` - Who is doing what
- `AttentionDecision` - What needs human attention
- See `src/lib/types/contracts.ts` for all types

---

## When You Need to Modify Contracts

**DON'T DO IT WITHOUT LEAD APPROVAL.**

If you truly need a change:
1. Write a proposal explaining:
   - What needs to change
   - Why it's necessary
   - Impact on other layers (core, E3, UI, E5)
2. Submit to Lead
3. Wait for approval
4. Lead will make the change (or approve you to make it)

---

## Useful Links

- `CONTRACT_DESIGN_DECISIONS.md` - Why decisions were made
- `CONTRACT_FIELD_REFERENCE.md` - Complete field reference
- `PHASE0_ACCEPTANCE.md` - Acceptance checklist
- `WRITE_SCOPE_LOCK.md` - What you can/can't modify
- `CONTRACT_REVIEW_REPORT.md` - Full review results

---

## Need Help?

- Ask the Lead Integrator first
- Check the examples in `src/myproj/core/contracts/examples.py`
- Look at tests in `tests/unit/contracts/` and `tests/integration/`
- Use the cheat sheets:
  - `AUTHORITY_SEMANTICS_CHEAT_SHEET`
  - `FIELD_NAMING_RULES`
