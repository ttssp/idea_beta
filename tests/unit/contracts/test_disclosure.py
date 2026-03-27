"""Disclosure contract tests."""

import pytest

from myproj.core.contracts.common import RiskLevel
from myproj.core.contracts.disclosure import (
    DisclosureField,
    DisclosureMode,
    DisclosurePolicy,
    DisclosurePreview,
)


class TestDisclosurePolicy:
    def test_template_mode_requires_template_text(self):
        with pytest.raises(ValueError):
            DisclosurePolicy(default_mode=DisclosureMode.TEMPLATE)

    def test_high_risk_resolves_to_full(self):
        policy = DisclosurePolicy(default_mode=DisclosureMode.SEMI)

        assert (
            policy.resolve_mode(
                is_external=True,
                is_sensitive_relationship=False,
                risk_level=RiskLevel.HIGH,
            )
            == DisclosureMode.FULL
        )

    def test_hidden_is_not_allowed_for_external_low_risk(self):
        policy = DisclosurePolicy(default_mode=DisclosureMode.HIDDEN)

        assert (
            policy.resolve_mode(
                is_external=True,
                is_sensitive_relationship=False,
                risk_level=RiskLevel.LOW,
            )
            == DisclosureMode.SEMI
        )


class TestDisclosurePreview:
    def test_preview_uses_policy_visibility(self):
        policy = DisclosurePolicy(default_mode=DisclosureMode.SEMI)
        preview = DisclosurePreview.from_policy(
            policy,
            is_external=True,
            is_sensitive_relationship=False,
            risk_level=RiskLevel.MEDIUM,
            rendered_text="Sent with agent assistance.",
        )

        assert preview.resolved_mode == DisclosureMode.SEMI
        assert DisclosureField.OWNER in preview.visible_fields
        assert preview.requires_recipient_notice

