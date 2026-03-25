
"""
Delegation Runtime Constants
"""
# 委托档位优先级（数值越大优先级越高）
DELEGATION_PRIORITY = {
    "thread": 100,
    "relationship": 50,
    "user_default": 20,
    "system_default": 10,
}

# 预算窗口类型
BUDGET_WINDOW_DAILY = "daily"
BUDGET_WINDOW_WEEKLY = "weekly"
BUDGET_WINDOW_MONTHLY = "monthly"
