
"""
Policy & Control Module

This module provides:
- Delegation Runtime: 委托档位管理、预算管理
- Policy Engine: 策略规则CRUD/匹配/优先级/冲突解决
- Approval Engine: 审批请求创建/审核/超时处理
- Risk Engine: 四层风险判断+合成决策+decision trace
- Kill Switch: 三层熔断（Global/Profile/Thread）
- Decision Trace: 每次决策的完整记录
"""

__version__ = "1.0.0"
