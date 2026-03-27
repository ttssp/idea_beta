"""
Governance Kernel - Communication OS

The future home for governance logic previously in policy_control.
This package handles:
- Delegation management
- Authority grants
- Policy evaluation
- Kill switch functionality
"""

from myproj.core.governance.delegation_service import DelegationServiceImpl
from myproj.core.governance.governance_service import GovernanceServiceImpl
from myproj.core.governance.interfaces import (
    GovernanceService,
    DelegationService,
)
from myproj.core.governance.kernel import GovernanceKernel
from myproj.core.governance.types import (
    GovernanceDecision,
    GovernanceResult,
)

__all__ = [
    "GovernanceService",
    "GovernanceServiceImpl",
    "DelegationService",
    "DelegationServiceImpl",
    "GovernanceKernel",
    "GovernanceResult",
    "GovernanceDecision",
]
