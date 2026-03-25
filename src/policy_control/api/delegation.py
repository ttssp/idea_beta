
"""
Delegation API

委托档位管理API
"""
from typing import List, Optional
from uuid import UUID
from dataclasses import dataclass

from ..common.constants import DelegationLevel
from ..delegation.models import DelegationProfile
from ..delegation.service import DelegationService


@dataclass
class SetThreadProfileRequest:
    profile_id: UUID


@dataclass
class SetRelationshipProfileRequest:
    profile_id: UUID


class DelegationAPI:
    """
    Delegation API

    Endpoints:
        POST /threads/{id}/delegation-profile
        POST /relationships/{id}/delegation-profile
        GET /delegation-profiles
    """

    def __init__(self, delegation_service: DelegationService):
        self.service = delegation_service

    def get_delegation_profiles(
        self,
        include_system: bool = True,
    ) -> List[DelegationProfile]:
        """
        GET /delegation-profiles

        查询所有可用委托档位
        """
        return self.service.list_profiles(include_system=include_system)

    def set_thread_delegation_profile(
        self,
        thread_id: UUID,
        request: SetThreadProfileRequest,
        bound_by: Optional[UUID] = None,
    ) -> bool:
        """
        POST /threads/{id}/delegation-profile

        设置线程委托档位
        """
        self.service.bind_thread_profile(
            thread_id=thread_id,
            profile_id=request.profile_id,
            bound_by=bound_by,
        )
        return True

    def set_relationship_delegation_profile(
        self,
        relationship_id: UUID,
        request: SetRelationshipProfileRequest,
        bound_by: Optional[UUID] = None,
    ) -> bool:
        """
        POST /relationships/{id}/delegation-profile

        设置关系默认委托档位
        """
        self.service.bind_relationship_profile(
            relationship_id=relationship_id,
            profile_id=request.profile_id,
            bound_by=bound_by,
        )
        return True
