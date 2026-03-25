
"""
Kill Switch API

熔断管理API
"""
from dataclasses import dataclass
from uuid import UUID

from ..common.constants import KillSwitchLevel
from ..kill_switch.models import KillSwitch
from ..kill_switch.service import KillSwitchService


@dataclass
class ActivateKillSwitchRequest:
    level: KillSwitchLevel
    level_id: UUID | None = None
    reason: str


class KillSwitchAPI:
    """
    Kill Switch API

    Endpoints:
        POST /kill-switches
        DELETE /kill-switches/{id}
        GET /kill-switches
    """

    def __init__(self, kill_switch_service: KillSwitchService):
        self.service = kill_switch_service

    def get_active_kill_switches(
        self,
        level: KillSwitchLevel | None = None,
    ) -> list[KillSwitch]:
        """
        GET /kill-switches

        查询当前生效的熔断
        """
        return self.service.get_active_switches(level=level)

    def activate_kill_switch(
        self,
        request: ActivateKillSwitchRequest,
        activated_by: UUID,
    ) -> KillSwitch:
        """
        POST /kill-switches

        创建熔断
        """
        return self.service.activate(
            level=request.level,
            level_id=request.level_id,
            reason=request.reason,
            activated_by=activated_by,
        )

    def deactivate_kill_switch(
        self,
        switch_id: UUID,
        deactivated_by: UUID,
    ) -> KillSwitch | None:
        """
        DELETE /kill-switches/{id}

        解除熔断
        """
        return self.service.deactivate(
            switch_id=switch_id,
            deactivated_by=deactivated_by,
        )
