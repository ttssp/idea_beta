"""Attention firewall contract tests."""

from uuid import uuid4

import pytest

from myproj.core.contracts.attention import AttentionDecision, AttentionDisposition


class TestAttentionDecision:
    def test_approval_required_must_require_human_action(self):
        with pytest.raises(ValueError):
            AttentionDecision(
                target_principal_id=uuid4(),
                disposition=AttentionDisposition.APPROVAL_REQUIRED,
                reason_code="approval_gate",
                summary="Needs approval.",
                requires_human_action=False,
            )

    def test_auto_resolvable_cannot_require_human_action(self):
        with pytest.raises(ValueError):
            AttentionDecision(
                target_principal_id=uuid4(),
                disposition=AttentionDisposition.AUTO_RESOLVABLE,
                reason_code="safe_auto",
                summary="Can be auto-resolved.",
                requires_human_action=True,
            )

