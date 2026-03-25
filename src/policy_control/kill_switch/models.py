
"""
Kill Switch Data Models
"""
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from ..common.constants import KillSwitchLevel


@dataclass
class KillSwitch:
    """熔断开关模型"""

    id: UUID = field(default_factory=uuid4)
    level: KillSwitchLevel = KillSwitchLevel.THREAD
    level_id: Optional[UUID] = None
    reason: str = ""
    activated_by: UUID = field(default_factory=uuid4)
    is_active: bool = True
    activated_at: datetime = field(default_factory=datetime.utcnow)
    deactivated_at: Optional[datetime] = None
    deactivated_by: Optional[UUID] = None

    def applies_to(
        self,
        level: KillSwitchLevel,
        level_id: Optional[UUID] = None,
    ) -&gt; bool:
        """
        检查此熔断是否适用于给定的级别

        熔断覆盖逻辑：Global &gt; Profile &gt; Thread
        """
        if not self.is_active:
            return False

        # Global熔断适用于所有
        if self.level == KillSwitchLevel.GLOBAL:
            return True

        # Profile熔断适用于同Profile及下属Thread
        if self.level == KillSwitchLevel.PROFILE:
            if level == KillSwitchLevel.PROFILE and self.level_id == level_id:
                return True
            if level == KillSwitchLevel.THREAD:
                # TODO: 需要检查Thread是否属于该Profile
                pass
            return False

        # Thread熔断仅适用于该Thread
        if self.level == KillSwitchLevel.THREAD:
            return level == KillSwitchLevel.THREAD and self.level_id == level_id

        return False
