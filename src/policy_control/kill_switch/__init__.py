
"""
Kill Switch Module

三层熔断（Global / Profile / Thread）
"""
from .models import KillSwitch
from .service import KillSwitchService

__all__ = ["KillSwitch", "KillSwitchService"]
