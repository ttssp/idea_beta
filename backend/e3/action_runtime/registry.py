
"""
Action Type Registry

Registry for action handler implementations.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class ActionHandler(ABC):
    """动作处理器基类"""

    @property
    @abstractmethod
    def action_type(self) -> str:
        """动作类型"""
        pass

    @abstractmethod
    async def validate(self, input_payload: dict[str, Any]) -> tuple[bool, str | None]:
        """
        验证输入参数

        Returns:
            (is_valid, error_message)
        """
        pass

    @abstractmethod
    async def execute(
        self,
        action_run_id: UUID,
        input_payload: dict[str, Any],
        context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        执行动作

        Args:
            action_run_id: ActionRun ID
            input_payload: 输入参数
            context: 执行上下文

        Returns:
            输出结果
        """
        pass


class ActionRegistry:
    """
    动作类型注册器

    用于注册和查找不同类型动作的处理器
    """

    def __init__(self):
        self._handlers: dict[str, ActionHandler] = {}

    def register(self, handler: ActionHandler):
        """注册动作处理器"""
        self._handlers[handler.action_type] = handler

    def get(self, action_type: str) -> ActionHandler | None:
        """获取动作处理器"""
        return self._handlers.get(action_type)

    def list_types(self) -> list[str]:
        """列出所有已注册的动作类型"""
        return list(self._handlers.keys())

    def has(self, action_type: str) -> bool:
        """检查动作类型是否已注册"""
        return action_type in self._handlers


# 全局注册器实例
registry = ActionRegistry()


def register_action(handler_class: type):
    """装饰器：注册动作处理器"""
    handler = handler_class()
    registry.register(handler)
    return handler_class

