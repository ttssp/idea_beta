
"""
Policy & Control Constants and Enums
"""
from enum import StrEnum


class DelegationLevel(StrEnum):
    """委托档位定义"""

    OBSERVE_ONLY = "observe_only"
    """只观察与建议，不起草不发送"""

    DRAFT_FIRST = "draft_first"
    """自动起草，但所有消息需人工确认"""

    APPROVE_TO_SEND = "approve_to_send"
    """低风险动作自动准备，用户一键审批后发出"""

    BOUNDED_AUTO = "bounded_auto"
    """在明确预算和动作边界内自动执行"""

    HUMAN_ONLY = "human_only"
    """该类关系或场景禁止代理主动介入"""


class Decision(StrEnum):
    """决策输出定义"""

    ALLOW = "allow"
    """允许自动执行"""

    DRAFT_ONLY = "draft_only"
    """仅允许起草，需人工确认后发送"""

    REQUIRE_APPROVAL = "require_approval"
    """需要审批后才能执行"""

    BOUNDED_EXECUTION = "bounded_execution"
    """在边界内自动执行"""

    ESCALATE_TO_HUMAN = "escalate_to_human"
    """升级给人工处理"""

    DENY = "deny"
    """拒绝执行"""


class RiskLevel(StrEnum):
    """风险等级定义"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(StrEnum):
    """审批状态定义"""

    PENDING = "pending"
    """待审批"""

    APPROVED = "approved"
    """已批准"""

    REJECTED = "rejected"
    """已拒绝"""

    MODIFIED = "modified"
    """已修改后批准"""

    TAKEN_OVER = "taken_over"
    """已接管"""

    CANCELLED = "cancelled"
    """已取消"""

    TIMEOUT = "timeout"
    """已超时"""


class KillSwitchLevel(StrEnum):
    """熔断级别定义"""

    GLOBAL = "global"
    """全局熔断"""

    PROFILE = "profile"
    """档位/配置熔断"""

    THREAD = "thread"
    """线程熔断"""


class PolicyEffect(StrEnum):
    """策略效果定义"""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    ESCALATE = "escalate"


class PolicyScope(StrEnum):
    """策略作用域定义"""

    GLOBAL = "global"
    PROFILE = "profile"
    RELATIONSHIP = "relationship"
    THREAD = "thread"


class RequestType(StrEnum):
    """审批请求类型"""

    MESSAGE_SEND = "message_send"
    ACTION_EXECUTE = "action_execute"
    BUDGET_INCREASE = "budget_increase"


class TimeoutAction(StrEnum):
    """超时动作"""

    ESCALATE = "escalate"
    DENY = "deny"
    AUTO_APPROVE = "auto_approve"


# 5种系统默认委托档位配置
SYSTEM_DELEGATION_PROFILES = [
    {
        "name": "observe_only",
        "display_name": "仅观察",
        "description": "系统只观察与建议，不起草不发送",
        "profile_level": DelegationLevel.OBSERVE_ONLY,
        "allowed_actions": [],
        "budget_config": None,
        "escalation_rules": {"all_actions": "escalate"},
        "is_system_defined": True,
    },
    {
        "name": "draft_first",
        "display_name": "优先起草",
        "description": "自动起草消息，但所有消息需人工确认",
        "profile_level": DelegationLevel.DRAFT_FIRST,
        "allowed_actions": ["draft_message"],
        "budget_config": None,
        "escalation_rules": {"send_message": "require_approval"},
        "is_system_defined": True,
    },
    {
        "name": "approve_to_send",
        "display_name": "审批发送",
        "description": "低风险动作自动准备，用户一键审批后发出",
        "profile_level": DelegationLevel.APPROVE_TO_SEND,
        "allowed_actions": ["draft_message", "prepare_action"],
        "budget_config": {"max_drafts_per_day": 20},
        "escalation_rules": {"high_risk": "escalate", "medium_risk": "require_approval"},
        "is_system_defined": True,
    },
    {
        "name": "bounded_auto",
        "display_name": "边界内自动",
        "description": "在明确预算和动作边界内自动执行",
        "profile_level": DelegationLevel.BOUNDED_AUTO,
        "allowed_actions": ["draft_message", "send_message", "schedule_followup"],
        "budget_config": {
            "max_messages_per_day": 10,
            "max_followups_per_thread": 3,
            "window_hours": 24,
        },
        "escalation_rules": {"high_risk": "escalate", "medium_risk": "require_approval"},
        "is_system_defined": True,
    },
    {
        "name": "human_only",
        "display_name": "仅人工",
        "description": "该类关系或场景禁止代理主动介入",
        "profile_level": DelegationLevel.HUMAN_ONLY,
        "allowed_actions": [],
        "budget_config": None,
        "escalation_rules": {"all_actions": "deny"},
        "is_system_defined": True,
    },
]
