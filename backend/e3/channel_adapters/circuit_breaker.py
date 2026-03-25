
"""
Circuit Breaker for Channel Adapters

Implements circuit breaker pattern for external API resilience.
"""

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

import pybreaker

from .base import ChannelError, RetryableChannelError

logger = logging.getLogger(__name__)


# 创建熔断器实例
# 配置：失败5次后开路，30秒后半开
email_circuit = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
)

calendar_circuit = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
)


class CircuitBreakerManager:
    """
    熔断器管理器

    管理多个渠道的熔断器状态
    """

    def __init__(self):
        self._circuits = {
            'email': email_circuit,
            'calendar': calendar_circuit
        }

    def get_circuit(self, channel: str) -> pybreaker.CircuitBreaker:
        """获取渠道对应的熔断器"""
        return self._circuits.get(channel, email_circuit)

    def get_state(self, channel: str) -> str:
        """获取熔断器状态"""
        circuit = self.get_circuit(channel)
        return circuit.state.name

    def is_open(self, channel: str) -> bool:
        """检查熔断器是否打开"""
        circuit = self.get_circuit(channel)
        return circuit.state == pybreaker.CircuitBreaker.OPEN

    def reset(self, channel: str):
        """重置熔断器"""
        circuit = self.get_circuit(channel)
        circuit.close()

    def force_open(self, channel: str):
        """强制打开熔断器"""
        circuit = self.get_circuit(channel)
        circuit.open()

    def get_all_states(self) -> dict[str, str]:
        """获取所有熔断器状态"""
        return {
            channel: circuit.state.name
            for channel, circuit in self._circuits.items()
        }


# 全局管理器实例
circuit_manager = CircuitBreakerManager()


def email_adapter_exception_handler(func: Callable) -> Callable:
    """
    Email适配器异常处理装饰器

    应用熔断器和异常分类
    """
    @wraps(func)
    @email_circuit
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except pybreaker.CircuitBreakerError:
            # 熔断器打开，返回降级响应
            logger.warning("Email circuit is open - request rejected")
            return {
                'status': 'degraded',
                'reason': 'email_service_unavailable',
                'message': 'Email service temporarily unavailable, message queued for retry'
            }
        except Exception as e:
            logger.error(f"Email adapter error: {e}", exc_info=True)

            # 区分可重试和不可重试错误
            if is_retryable_email_error(e):
                raise RetryableChannelError(str(e)) from e
            else:
                raise ChannelError(str(e)) from e

    return wrapper


def calendar_adapter_exception_handler(func: Callable) -> Callable:
    """
    Calendar适配器异常处理装饰器
    """
    @wraps(func)
    @calendar_circuit
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except pybreaker.CircuitBreakerError:
            logger.warning("Calendar circuit is open - request rejected")
            return {
                'status': 'degraded',
                'reason': 'calendar_service_unavailable'
            }
        except Exception as e:
            logger.error(f"Calendar adapter error: {e}", exc_info=True)

            if is_retryable_calendar_error(e):
                raise RetryableChannelError(str(e)) from e
            else:
                raise ChannelError(str(e)) from e

    return wrapper


def is_retryable_email_error(error: Exception) -> bool:
    """
    判断Email错误是否可重试
    """
    error_str = str(error).lower()

    retryable_keywords = [
        'timeout',
        'timed out',
        'connection',
        'server error',
        '500',
        '502',
        '503',
        '504',
        'service unavailable',
        'rate limit',
        '429',
        'temporary'
    ]

    for keyword in retryable_keywords:
        if keyword in error_str:
            return True

    return False


def is_retryable_calendar_error(error: Exception) -> bool:
    """
    判断Calendar错误是否可重试
    """
    # 使用与Email相同的逻辑
    return is_retryable_email_error(error)


def get_circuit_metrics() -> dict[str, Any]:
    """
    获取熔断器指标（用于监控）
    """
    metrics = {}

    for channel, circuit in [('email', email_circuit), ('calendar', calendar_circuit)]:
        metrics[channel] = {
            'state': circuit.state.name,
            'fail_counter': circuit.fail_counter,
            'fail_max': circuit.fail_max,
            'open_at': circuit.open_at.isoformat() if circuit.open_at else None,
            'timeout_seconds': circuit.reset_timeout,
        }

    return metrics
