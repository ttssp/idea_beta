# Contract Field Reference

## Field Naming Rules

1. **Use owner/delegate/author/approver/executor exactly** - do not invent synonyms
2. **Use \*_id or \*_ids** for UUID-bearing fields, keep stable across contracts
3. **Use \*_mode** for enum-based behavioral switches (disclosure_mode, execution_mode)
4. **Use risk_level** for resolved posture, **reason_codes** for machine-readable causes
5. **Use authority_source** to point at the AuthorityGrant that permitted an action

---

## ActorRef

A stable actor reference used across sender, authority, and action contracts.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `principal_id` | UUID | Yes | Unique identifier for this actor |
| `display_name` | str (max 200) | Yes | Human-readable name |
| `principal_kind` | PrincipalKind | Yes | What kind of principal this is |
| `affiliation_id` | UUID | No | Organization/group this actor belongs to |
| `affiliation_name` | str (max 200) | No | Display name for affiliation |
| `is_human_controlled` | bool | Yes | Whether a human is ultimately in control |
| `metadata` | dict | No | Extended data |

**PrincipalKind Values**:
- `HUMAN` - Natural person
- `PERSONAL_AGENT` - Agent acting on behalf of one human
- `ORGANIZATION_AGENT` - Agent acting on behalf of an organization
- `SERVICE_AGENT` - Infrastructure/service agent
- `EXTERNAL_PARTICIPANT` - External counterparty
- `PUBLIC_SERVICE_AGENT` - Government/public service agent

---

## AuthorityGrant

A first-class record of who may act on whose behalf and under what bounds.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `authority_grant_id` | UUID | Yes | Unique grant ID |
| `grantor` | ActorRef | Yes | Who is giving authority |
| `delegate` | ActorRef | Yes | Who is receiving authority |
| `delegation_mode` | DelegationMode | Yes | Authority level granted |
| `allowed_actions` | list[str] | No | Action type whitelist |
| `requires_approval_for` | list[str] | No | Actions needing human approval |
| `relationship_scope` | RelationshipScope | Yes | Which relationships are in scope |
| `thread_scope` | ThreadScope | Yes | Which threads are in scope |
| `max_risk_level` | RiskLevel | Yes | Maximum allowed risk |
| `disclosure_policy` | DisclosurePolicy | Yes | How to disclose delegation |
| `granted_at` | datetime | Yes | When grant was created |
| `expires_at` | datetime | No | When grant expires |
| `revoked_at` | datetime | No | When grant was revoked |
| `status` | AuthorityGrantStatus | Yes | Current lifecycle state |
| `metadata` | dict | No | Extended data |

**DelegationMode Values**:
- `OBSERVE_ONLY` - Read-only access
- `DRAFT_FIRST` - May draft but not send
- `APPROVE_TO_SEND` - May prepare with approval gate
- `BOUNDED_AUTO` - May auto-execute within bounds
- `HUMAN_ONLY` - No delegation allowed

**AuthorityGrantStatus Values**:
- `ACTIVE` - Currently usable
- `REVOKED` - Manually revoked
- `EXPIRED` - Past expiration
- `SUSPENDED` - Temporarily paused

**Invariants**:
- grantor ≠ delegate
- requires_approval_for ⊆ allowed_actions
- expires_at (if set) > granted_at
- revoked_at only set if status ≠ ACTIVE

---

## RelationshipScope

The relationship slice in which a grant may be exercised.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `include_all` | bool | Yes | If true, all relationships allowed |
| `relationship_ids` | list[UUID] | No | Specific relationships allowed |
| `relationship_classes` | list[str] | No | Relationship classes allowed |

**Invariants**:
- If include_all=true: relationship_ids and relationship_classes must be empty
- If include_all=false: at least one selector required

---

## ThreadScope

The thread slice in which a grant may be exercised.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `include_all` | bool | Yes | If true, all threads allowed |
| `thread_ids` | list[UUID] | No | Specific threads allowed |

**Invariants**:
- If include_all=true: thread_ids must be empty
- If include_all=false: at least one thread_id required

---

## SenderStack

Who is represented, who drafted, who approved, and who executed an action.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `owner` | ActorRef | Yes | Ultimately represented human/organization |
| `delegate` | ActorRef | No | Agent acting on behalf at runtime |
| `author` | ActorRef | Yes | Who drafted content/prepared payload |
| `approver` | ActorRef | No | Who explicitly approved (if any) |
| `executor` | ActorRef | No | System/service that delivered/enacted |
| `disclosure_mode` | DisclosureMode | Yes | How much to disclose externally |
| `authority_source` | UUID | Yes | AuthorityGrant that permitted this |
| `authority_label` | str (max 200) | No | Human-readable policy label |
| `representation_note` | str (max 500) | No | Additional context |
| `metadata` | dict | No | Extended data |

**Invariants**:
- If delegate present: delegate ≠ owner

**Methods**:
- `visible_actor_ids()` → list[UUID] - Ordered, deduplicated actor IDs

---

## DisclosurePolicy

Rules that resolve how an action should be disclosed externally.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `policy_id` | UUID | Yes | Unique policy ID |
| `default_mode` | DisclosureMode | Yes | Starting disclosure mode |
| `template_text` | str (max 500) | No | Template for TEMPLATE mode |
| `require_at_least_semi_for_external` | bool | Yes | External ≥ SEMI |
| `require_full_for_sensitive_relationships` | bool | Yes | Sensitive → FULL |
| `require_full_for_high_risk` | bool | Yes | HIGH/CRITICAL → FULL |
| `allow_hidden_only_for_internal_low_risk` | bool | Yes | HIDDEN restricted |
| `mode_configs` | list[DisclosureModeConfig] | Yes | Per-mode configs |
| `metadata` | dict | No | Extended data |

**DisclosureMode Values**:
- `FULL` - Explicitly shows agent participation and chain
- `SEMI` - Indicates delegated assistance without full chain
- `TEMPLATE` - Follows policy-defined disclosure template
- `HIDDEN` - Only allowed in narrow low-risk internal cases

**Invariants**:
- mode_configs must cover all 4 DisclosureMode values
- If default_mode=TEMPLATE: template_text required

**Methods**:
- `config_for(mode: DisclosureMode)` → DisclosureModeConfig
- `resolve_mode(*, is_external, is_sensitive_relationship, risk_level)` → DisclosureMode

---

## DisclosureModeConfig

Recipient-visible behavior for one disclosure mode.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mode` | DisclosureMode | Yes | Which mode this configures |
| `visible_fields` | list[DisclosureField] | Yes | Fields recipient may see |
| `requires_recipient_notice` | bool | Yes | Whether to show notice |

**DisclosureField Values**:
- `OWNER`
- `DELEGATE`
- `AUTHOR`
- `APPROVER`
- `EXECUTOR`
- `AUTHORITY_SOURCE`

---

## DisclosurePreview

Resolved disclosure information ready for approval or execution surfaces.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `policy_id` | UUID | Yes | Policy used to resolve |
| `resolved_mode` | DisclosureMode | Yes | Final disclosure mode |
| `visible_fields` | list[DisclosureField] | Yes | Fields to show recipient |
| `rendered_text` | str (max 1000) | No | Human-readable disclosure |
| `requires_recipient_notice` | bool | Yes | Whether to show notice |

**Factory Method**:
```python
DisclosurePreview.from_policy(
    policy: DisclosurePolicy,
    *,
    is_external: bool,
    is_sensitive_relationship: bool,
    risk_level: RiskLevel,
    rendered_text: str | None = None,
) → DisclosurePreview
```

---

## AttentionDecision

A structured result from the future inbox or attention firewall.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `decision_id` | UUID | Yes | Unique decision ID |
| `target_principal_id` | UUID | Yes | Who this decision is for |
| `disposition` | AttentionDisposition | Yes | What should happen |
| `reason_code` | str (1-100) | Yes | Machine-readable reason |
| `summary` | str (1-500) | Yes | Human-readable summary |
| `related_thread_id` | UUID | No | Associated thread |
| `related_action_id` | UUID | No | Associated action |
| `requires_human_action` | bool | Yes | Whether human must act |
| `notify_now` | bool | Yes | Whether to notify immediately |
| `due_at` | datetime | No | When action is due |
| `suppress_until` | datetime | No | Hide until this time |
| `metadata` | dict | No | Extended data |

**AttentionDisposition Values**:
- `MUST_REVIEW_NOW` - Human must review immediately
- `APPROVAL_REQUIRED` - Human must approve/reject
- `INFORMATIONAL_ONLY` - For information, no action needed
- `SUMMARY_ONLY` - Only show summary, hide details
- `AUTO_RESOLVABLE` - System can handle automatically
- `DIRECT_HUMAN_REQUIRED` - Human must be present directly

**Invariants**:
- MUST_REVIEW_NOW, APPROVAL_REQUIRED, DIRECT_HUMAN_REQUIRED → requires_human_action=true
- AUTO_RESOLVABLE → requires_human_action=false
- If suppress_until and due_at: suppress_until ≤ due_at

---

## ActionEnvelope

A stable action contract shared across planning, approval, and execution.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `envelope_id` | UUID | Yes | Unique envelope ID |
| `action_type` | str (1-100) | Yes | What kind of action |
| `action_label` | str (max 200) | No | Human-readable label |
| `thread` | ThreadContextRef | Yes | Thread context |
| `relationships` | RelationshipContextRef | Yes | Relationship context |
| `sender_stack` | SenderStack | Yes | Who is doing this |
| `disclosure_preview` | DisclosurePreview | Yes | How to disclose |
| `target` | ActionTarget | Yes | Where to send/act |
| `risk_posture` | RiskPosture | Yes | Risk assessment |
| `execution_mode` | ActionExecutionMode | Yes | How to execute |
| `approval_request_id` | UUID | No | Associated approval |
| `idempotency_key` | str (max 255) | No | Idempotency key |
| `payload` | dict | No | Action-specific data |
| `metadata` | dict | No | Extended data |

**ActionExecutionMode Values**:
- `PREPARE_ONLY` - Don't execute, just prepare
- `EXECUTE_IMMEDIATELY` - Execute right away
- `EXECUTE_AFTER_APPROVAL` - Wait for approval first

**Invariants**:
- If execution_mode=EXECUTE_AFTER_APPROVAL: risk_posture.requires_approval=true OR approval_request_id set

---

## ThreadContextRef

Thread context needed by downstream systems.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `thread_id` | UUID | Yes | Thread identifier |
| `objective` | str (max 2000) | No | Thread objective |
| `thread_status` | str (max 100) | No | Current status |
| `participant_ids` | list[UUID] | No | Thread participants |
| `relationship_ids` | list[UUID] | No | Related relationships |

---

## RelationshipContextRef

Relationship context for policy and risk evaluation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `relationship_ids` | list[UUID] | No | Specific relationship IDs |
| `relationship_classes` | list[str] | No | Relationship classes |
| `is_sensitive` | bool | Yes | Whether sensitive |

---

## ActionTarget

Who or what the action is aimed at.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `channel` | ChannelKind | Yes | Which channel to use |
| `recipient_ids` | list[UUID] | No | Recipient principal IDs |
| `recipient_handles` | list[str] | No | External handles (emails, etc.) |
| `subject` | str (max 500) | No | Subject/title |
| `metadata` | dict | No | Extended data |

**ChannelKind Values**:
- `INTERNAL` - Internal system only
- `EMAIL` - Email
- `CALENDAR` - Calendar invites/events
- `SMS` - Text message
- `SLACK` - Slack
- `TEAMS` - Microsoft Teams
- `CUSTOM` - Custom channel

**Invariants**:
- At least one of recipient_ids or recipient_handles required

---

## RiskPosture

Risk information attached to a proposed action.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `risk_level` | RiskLevel | Yes | Overall risk level |
| `requires_approval` | bool | Yes | Whether approval needed |
| `reason_codes` | list[str] | No | Machine-readable reasons |
| `summary` | str (max 500) | No | Human-readable summary |

**RiskLevel Values**:
- `LOW` - No approval needed, safe to auto-execute
- `MEDIUM` - May need approval depending on policy
- `HIGH` - Requires approval, full disclosure
- `CRITICAL` - Requires human, full disclosure, audit

---

## Version Compatibility

### Backward Compatibility Guarantees

- Fields marked "Required" will never be removed
- Enum values will never be deleted (may be deprecated)
- New fields will always be optional with defaults
- Pydantic models use `extra="forbid"` to catch mismatches

### Forward Compatibility Practices

- Check for optional fields before using
- Use `model.model_dump(exclude_none=True)` when serializing
- Use `model_copy(update=...)` to create modified copies
- Never rely on field ordering

---

## Import Pattern

Always import from the package, not individual modules:

```python
# GOOD
from myproj.core.contracts import (
    AuthorityGrant,
    SenderStack,
    DisclosurePolicy,
    ActionEnvelope,
    AttentionDecision,
    RiskLevel,
    DisclosureMode,
)

# BAD - Don't do this
from myproj.core.contracts.authority import AuthorityGrant
from myproj.core.contracts.sender_stack import SenderStack
```
