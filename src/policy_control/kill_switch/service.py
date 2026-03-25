
"""
Kill Switch Service

熔断管理、联动逻辑
"""
from typing import List, Optional, Dict, Callable
from uuid import UUID
from datetime import datetime

from ..common.constants import KillSwitchLevel
from ..common.exceptions import KillSwitchActiveError
from .models import KillSwitch


class KillSwitchService:
    """
    熔断服务

    支持三层熔断：
    - Global：全局熔断
    - Profile：档位/配置熔断
    - Thread：线程熔断

    检查逻辑：Global > Profile > Thread（父级熔断覆盖子级）
    """

    def __init__(self):
        self._switches: Dict[UUID, KillSwitch] = {}
        self._on_activated_callbacks: List[Callable] = []
        self._on_deactivated_callbacks: List[Callable] = []

    def on_activated(self, callback: Callable):
        """注册熔断激活回调"""
        self._on_activated_callbacks.append(callback)

    def on_deactivated(self, callback: Callable):
        """注册熔断解除回调"""
        self._on_deactivated_callbacks.append(callback)

    def activate(
        self,
        level: KillSwitchLevel,
        reason: str,
        activated_by: UUID,
        level_id: Optional[UUID] = None,
    ) -> KillSwitch:
        """
        激活熔断

        Args:
            level: 熔断级别
            reason: 原因
            activated_by: 激活者ID
            level_id: 级别ID（对于Profile/Thread级别）

        Returns:
            激活的熔断开关
        """
        # 检查是否已有同级别/同ID的活跃熔断
        existing = self._find_existing_active(level, level_id)
        if existing:
            return existing

        switch = KillSwitch(
            level=level,
            level_id=level_id,
            reason=reason,
            activated_by=activated_by,
            is_active=True,
            activated_at=datetime.utcnow(),
        )
        self._switches[switch.id] = switch

        # 触发回调
        for callback in self._on_activated_callbacks:
            try:
                callback(switch)
            except Exception:
                pass

        return switch

    def deactivate(
        self,
        switch_id: UUID,
        deactivated_by: UUID,
    ) -> Optional[KillSwitch]:
        """
        解除熔断

        Args:
            switch_id: 熔断开关ID
            deactivated_by: 解除者ID

        Returns:
            解除的熔断开关
        """
        switch = self._switches.get(switch_id)
        if not switch or not switch.is_active:
            return None

        switch.is_active = False
        switch.deactivated_at = datetime.utcnow()
        switch.deactivated_by = deactivated_by

        # 触发回调
        for callback in self._on_deactivated_callbacks:
            try:
                callback(switch)
            except Exception:
                pass

        return switch

    def deactivate_all(
        self,
        level: Optional[KillSwitchLevel] = None,
        deactivated_by: Optional[UUID] = None,
    ) -> List[KillSwitch]:
        """
        批量解除熔断

        Args:
            level: 按级别过滤
            deactivated_by: 解除者ID

        Returns:
            解除的熔断开关列表
        """
        deactivated = []
        for switch in self._switches.values():
            if not switch.is_active:
                continue
            if level and switch.level != level:
                continue

            switch.is_active = False
            switch.deactivated_at = datetime.utcnow()
            switch.deactivated_by = deactivated_by
            deactivated.append(switch)

            for callback in self._on_deactivated_callbacks:
                try:
                    callback(switch)
                except Exception:
                    pass

        return deactivated

    def check(
        self,
        level: KillSwitchLevel,
        level_id: Optional[UUID] = None,
    ) -> bool:
        """
        检查是否有熔断生效

        检查逻辑：Global > Profile > Thread（父级熔断覆盖子级）

        Args:
            level: 要检查的级别
            level_id: 级别ID

        Returns:
            True if 有熔断生效
        """
        # 先检查Global级熔断
        for switch in self._switches.values():
            if switch.is_active and switch.level == KillSwitchLevel.GLOBAL:
                return True

        # 再检查Profile级熔断
        if level in [KillSwitchLevel.PROFILE, KillSwitchLevel.THREAD]:
            for switch in self._switches.values():
                if switch.is_active and switch.level == KillSwitchLevel.PROFILE:
                    # 如果检查的是Profile级别，直接匹配
                    if level == KillSwitchLevel.PROFILE and switch.level_id == level_id:
                        return True
                    # 如果检查的是Thread级别，需要关联检查（这里简化处理）
                    pass

        # 最后检查Thread级熔断
        if level == KillSwitchLevel.THREAD:
            for switch in self._switches.values():
                if (
                    switch.is_active
                    and switch.level == KillSwitchLevel.THREAD
                    and switch.level_id == level_id
                ):
                    return True

        return False

    def get_active_switches(
        self,
        level: Optional[KillSwitchLevel] = None,
    ) -> List[KillSwitch]:
        """
        获取当前生效的熔断

        Args:
            level: 按级别过滤

        Returns:
            活跃的熔断开关列表
        """
        switches = [s for s in self._switches.values() if s.is_active]
        if level:
            switches = [s for s in switches if s.level == level]
        return switches

    def get_switch(self, switch_id: UUID) -> Optional[KillSwitch]:
        """获取熔断开关"""
        return self._switches.get(switch_id)

    def ensure_not_triggered(
        self,
        level: KillSwitchLevel,
        level_id: Optional[UUID] = None,
    ):
        """
        确保没有熔断触发，否则抛出异常

        Raises:
            KillSwitchActiveError: 如果有熔断生效
        """
        if self.check(level, level_id):
            raise KillSwitchActiveError(
                f"Kill switch active for {level.value}"
                + (f": {level_id}" if level_id else "")
            )

    def _find_existing_active(
        self,
        level: KillSwitchLevel,
        level_id: Optional[UUID] = None,
    ) -> Optional[KillSwitch]:
        """查找已存在的活跃熔断"""
        for switch in self._switches.values():
            if not switch.is_active:
                continue
            if switch.level != level:
                continue
            if level in [KillSwitchLevel.PROFILE, KillSwitchLevel.THREAD]:
                if switch.level_id == level_id:
                    return switch
            else:  # GLOBAL
                return switch
        return None
