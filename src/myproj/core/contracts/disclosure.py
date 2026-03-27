"""Disclosure policy contracts for delegated communication."""

from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import Field, model_validator

from myproj.core.contracts.common import ContractModel, RiskLevel


class DisclosureMode(StrEnum):
    """How much of the delegated communication chain is visible to recipients."""

    FULL = "full"
    SEMI = "semi"
    TEMPLATE = "template"
    HIDDEN = "hidden"


class DisclosureField(StrEnum):
    """Fields a recipient may be allowed to inspect."""

    OWNER = "owner"
    DELEGATE = "delegate"
    AUTHOR = "author"
    APPROVER = "approver"
    EXECUTOR = "executor"
    AUTHORITY_SOURCE = "authority_source"


class DisclosureModeConfig(ContractModel):
    """Recipient-visible behavior for one disclosure mode."""

    mode: DisclosureMode
    visible_fields: list[DisclosureField] = Field(default_factory=list)
    requires_recipient_notice: bool = True

    @model_validator(mode="after")
    def _dedupe_fields(self) -> "DisclosureModeConfig":
        self.visible_fields = list(dict.fromkeys(self.visible_fields))
        return self


def default_mode_configs() -> list[DisclosureModeConfig]:
    """Default recipient-visible fields per mode."""
    return [
        DisclosureModeConfig(
            mode=DisclosureMode.FULL,
            visible_fields=[
                DisclosureField.OWNER,
                DisclosureField.DELEGATE,
                DisclosureField.AUTHOR,
                DisclosureField.APPROVER,
                DisclosureField.EXECUTOR,
                DisclosureField.AUTHORITY_SOURCE,
            ],
            requires_recipient_notice=True,
        ),
        DisclosureModeConfig(
            mode=DisclosureMode.SEMI,
            visible_fields=[
                DisclosureField.OWNER,
                DisclosureField.DELEGATE,
                DisclosureField.AUTHOR,
            ],
            requires_recipient_notice=True,
        ),
        DisclosureModeConfig(
            mode=DisclosureMode.TEMPLATE,
            visible_fields=[
                DisclosureField.OWNER,
                DisclosureField.DELEGATE,
            ],
            requires_recipient_notice=True,
        ),
        DisclosureModeConfig(
            mode=DisclosureMode.HIDDEN,
            visible_fields=[],
            requires_recipient_notice=False,
        ),
    ]


class DisclosurePolicy(ContractModel):
    """Rules that resolve how an action should be disclosed externally."""

    policy_id: UUID = Field(default_factory=uuid4)
    default_mode: DisclosureMode = DisclosureMode.SEMI
    template_text: str | None = Field(None, max_length=500)
    require_at_least_semi_for_external: bool = True
    require_full_for_sensitive_relationships: bool = True
    require_full_for_high_risk: bool = True
    allow_hidden_only_for_internal_low_risk: bool = True
    mode_configs: list[DisclosureModeConfig] = Field(default_factory=default_mode_configs)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_policy(self) -> "DisclosurePolicy":
        seen_modes = {config.mode for config in self.mode_configs}
        missing_modes = set(DisclosureMode) - seen_modes
        if missing_modes:
            missing = ", ".join(sorted(mode.value for mode in missing_modes))
            raise ValueError(f"mode_configs must cover every disclosure mode; missing: {missing}")

        if self.default_mode == DisclosureMode.TEMPLATE and not self.template_text:
            raise ValueError("template_text is required when default_mode is template")

        return self

    def config_for(self, mode: DisclosureMode) -> DisclosureModeConfig:
        """Return the mode configuration for the given disclosure mode."""
        for config in self.mode_configs:
            if config.mode == mode:
                return config
        raise KeyError(f"No disclosure mode config found for {mode.value}")

    def resolve_mode(
        self,
        *,
        is_external: bool,
        is_sensitive_relationship: bool,
        risk_level: RiskLevel,
    ) -> DisclosureMode:
        """Resolve the final disclosure mode from defaults and runtime context."""
        mode = self.default_mode

        if self.require_full_for_high_risk and risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            mode = DisclosureMode.FULL

        if self.require_full_for_sensitive_relationships and is_sensitive_relationship:
            mode = DisclosureMode.FULL

        if is_external and self.require_at_least_semi_for_external and mode == DisclosureMode.HIDDEN:
            mode = DisclosureMode.SEMI

        if (
            mode == DisclosureMode.HIDDEN
            and self.allow_hidden_only_for_internal_low_risk
            and (is_external or risk_level != RiskLevel.LOW)
        ):
            mode = DisclosureMode.SEMI

        return mode


class DisclosurePreview(ContractModel):
    """Resolved disclosure information ready for approval or execution surfaces."""

    policy_id: UUID
    resolved_mode: DisclosureMode
    visible_fields: list[DisclosureField] = Field(default_factory=list)
    rendered_text: str | None = Field(None, max_length=1000)
    requires_recipient_notice: bool

    @classmethod
    def from_policy(
        cls,
        policy: DisclosurePolicy,
        *,
        is_external: bool,
        is_sensitive_relationship: bool,
        risk_level: RiskLevel,
        rendered_text: str | None = None,
    ) -> "DisclosurePreview":
        """Create a preview based on a policy and runtime context."""
        resolved_mode = policy.resolve_mode(
            is_external=is_external,
            is_sensitive_relationship=is_sensitive_relationship,
            risk_level=risk_level,
        )
        mode_config = policy.config_for(resolved_mode)
        return cls(
            policy_id=policy.policy_id,
            resolved_mode=resolved_mode,
            visible_fields=mode_config.visible_fields,
            rendered_text=rendered_text,
            requires_recipient_notice=mode_config.requires_recipient_notice,
        )

