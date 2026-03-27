
"""
Policy & Control Module - COMPATIBILITY LAYER

This module is being migrated to src/myproj/core/governance,
src/myproj/core/approvals, and src/myproj/core/risk.

This compatibility layer re-exports from the new locations.
"""

__version__ = "2.0.0"

# Re-exports from new governance packages
from myproj.core.governance import (
    GovernanceService,
    GovernanceServiceImpl,
    DelegationService,
    DelegationServiceImpl,
    GovernanceKernel,
    GovernanceResult,
    GovernanceDecision,
)

from myproj.core.approvals import (
    ApprovalService,
    ApprovalRequest,
    ApprovalResolution,
    ApprovalStatus,
    ApprovalAction,
)

from myproj.core.risk import (
    RiskSynthesizer,
    RiskReason,
    RiskEvaluation,
)

__all__ = [
    # Governance
    "GovernanceService",
    "GovernanceServiceImpl",
    "DelegationService",
    "DelegationServiceImpl",
    "GovernanceKernel",
    "GovernanceResult",
    "GovernanceDecision",
    # Approvals
    "ApprovalService",
    "ApprovalRequest",
    "ApprovalResolution",
    "ApprovalStatus",
    "ApprovalAction",
    # Risk
    "RiskSynthesizer",
    "RiskReason",
    "RiskEvaluation",
]
