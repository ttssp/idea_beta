"""
Tests for governance landing zones.

These tests verify that the new governance, approvals, and risk
packages are properly structured and can be imported.
"""

import pytest


class TestGovernanceImports:
    """Test that governance package can be imported."""

    def test_can_import_governance_package(self):
        """Can import from myproj.core.governance."""
        from myproj.core.governance import (
            GovernanceService,
            GovernanceServiceImpl,
            DelegationService,
            DelegationServiceImpl,
            GovernanceKernel,
            GovernanceResult,
            GovernanceDecision,
        )

        assert GovernanceService is not None
        assert GovernanceServiceImpl is not None
        assert DelegationService is not None
        assert DelegationServiceImpl is not None
        assert GovernanceKernel is not None
        assert GovernanceResult is not None
        assert GovernanceDecision is not None

    def test_can_import_governance_types(self):
        """Can import governance types."""
        from myproj.core.governance.types import (
            GovernanceDecision,
            GovernanceResult,
        )

        assert GovernanceDecision.ALLOW == "allow"
        assert GovernanceDecision.DENY == "deny"
        assert GovernanceDecision.REQUIRE_APPROVAL == "require_approval"
        assert GovernanceDecision.ESCALATE == "escalate"

    def test_can_create_governance_result(self):
        """Can create a GovernanceResult."""
        from myproj.core.governance.types import (
            GovernanceDecision,
            GovernanceResult,
        )
        from myproj.core.contracts import RiskLevel

        result = GovernanceResult(
            decision=GovernanceDecision.ALLOW,
            reason_code="test_ok",
            reason_description="Everything is okay",
            risk_level=RiskLevel.LOW,
        )

        assert result.is_allowed
        assert not result.requires_approval
        assert not result.should_escalate
        assert not result.is_denied
        assert result.reason_code == "test_ok"

    def test_can_import_delegation_service(self):
        """Can import and instantiate DelegationServiceImpl."""
        from myproj.core.governance import DelegationServiceImpl
        from myproj.core.contracts.examples import AUTHORITY_GRANT_EXAMPLE

        service = DelegationServiceImpl()
        service.add_grant(AUTHORITY_GRANT_EXAMPLE)

        grant = service.get_active_grant_for_delegate(
            grantor_id=AUTHORITY_GRANT_EXAMPLE.grantor.principal_id,
            delegate_id=AUTHORITY_GRANT_EXAMPLE.delegate.principal_id,
        )

        assert grant is not None
        assert grant.authority_grant_id == AUTHORITY_GRANT_EXAMPLE.authority_grant_id


class TestApprovalsImports:
    """Test that approvals package can be imported."""

    def test_can_import_approvals_package(self):
        """Can import from myproj.core.approvals."""
        from myproj.core.approvals import (
            ApprovalService,
            ApprovalRequest,
            ApprovalResolution,
            ApprovalStatus,
            ApprovalAction,
        )

        assert ApprovalService is not None
        assert ApprovalRequest is not None
        assert ApprovalResolution is not None
        assert ApprovalStatus is not None
        assert ApprovalAction is not None

    def test_can_import_approvals_types(self):
        """Can import approval types."""
        from myproj.core.approvals.types import (
            ApprovalStatus,
            ApprovalAction,
        )

        assert ApprovalStatus.PENDING == "pending"
        assert ApprovalStatus.APPROVED == "approved"
        assert ApprovalStatus.REJECTED == "rejected"

        assert ApprovalAction.APPROVE == "approve"
        assert ApprovalAction.REJECT == "reject"
        assert ApprovalAction.MODIFY == "modify"
        assert ApprovalAction.TAKE_OVER == "take_over"


class TestRiskImports:
    """Test that risk package can be imported."""

    def test_can_import_risk_package(self):
        """Can import from myproj.core.risk."""
        from myproj.core.risk import (
            RiskSynthesizer,
            RiskReason,
            RiskEvaluation,
        )

        assert RiskSynthesizer is not None
        assert RiskReason is not None
        assert RiskEvaluation is not None

    def test_can_import_risk_types(self):
        """Can import risk types."""
        from myproj.core.risk.types import RiskFactor

        assert RiskFactor.CONTENT == "content"
        assert RiskFactor.RELATIONSHIP == "relationship"
        assert RiskFactor.ACTION == "action"
        assert RiskFactor.EXTERNAL == "external"


class TestPolicyControlCompatibility:
    """Test that policy_control compatibility shims work."""

    def test_policy_control_reexports_governance(self):
        """policy_control re-exports governance types."""
        import policy_control

        assert hasattr(policy_control, "GovernanceService")
        assert hasattr(policy_control, "DelegationService")
        assert hasattr(policy_control, "GovernanceKernel")
        assert hasattr(policy_control, "GovernanceResult")
        assert hasattr(policy_control, "GovernanceDecision")

    def test_policy_control_reexports_approvals(self):
        """policy_control re-exports approval types."""
        import policy_control

        assert hasattr(policy_control, "ApprovalService")
        assert hasattr(policy_control, "ApprovalRequest")
        assert hasattr(policy_control, "ApprovalResolution")
        assert hasattr(policy_control, "ApprovalStatus")
        assert hasattr(policy_control, "ApprovalAction")

    def test_policy_control_reexports_risk(self):
        """policy_control re-exports risk types."""
        import policy_control

        assert hasattr(policy_control, "RiskSynthesizer")
        assert hasattr(policy_control, "RiskReason")
        assert hasattr(policy_control, "RiskEvaluation")
