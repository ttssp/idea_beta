
"""
Policy &amp; Control Exceptions
"""


class PolicyControlError(Exception):
    """Policy &amp; Control基础异常"""

    pass


class PolicyRuleConflictError(PolicyControlError):
    """策略规则冲突"""

    pass


class ApprovalStateTransitionError(PolicyControlError):
    """审批状态流转错误"""

    pass


class BudgetExceededError(PolicyControlError):
    """预算超限"""

    pass


class KillSwitchActiveError(PolicyControlError):
    """熔断已激活"""

    pass


class InvalidDelegationProfileError(PolicyControlError):
    """无效的委托档位"""

    pass
