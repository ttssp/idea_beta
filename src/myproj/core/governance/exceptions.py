"""
Governance exceptions.
"""


class GovernanceError(Exception):
    """Base exception for governance errors."""

    pass


class AuthorityGrantNotFoundError(GovernanceError):
    """Raised when an authority grant is not found."""

    def __init__(self, grant_id: str):
        super().__init__(f"Authority grant not found: {grant_id}")


class GrantRevokedError(GovernanceError):
    """Raised when trying to use a revoked grant."""

    def __init__(self, grant_id: str):
        super().__init__(f"Authority grant is revoked: {grant_id}")


class GrantExpiredError(GovernanceError):
    """Raised when trying to use an expired grant."""

    def __init__(self, grant_id: str):
        super().__init__(f"Authority grant is expired: {grant_id}")


class ActionNotAllowedError(GovernanceError):
    """Raised when an action is not allowed by a grant."""

    def __init__(self, action_type: str, grant_id: str):
        super().__init__(f"Action '{action_type}' not allowed by grant {grant_id}")


class RiskLevelExceededError(GovernanceError):
    """Raised when risk level exceeds grant's maximum."""

    def __init__(self, risk_level: str, max_risk: str):
        super().__init__(f"Risk level {risk_level} exceeds max {max_risk}")


class ApprovalRequiredError(GovernanceError):
    """Raised when an action requires approval."""

    def __init__(self, reason: str):
        super().__init__(f"Approval required: {reason}")
