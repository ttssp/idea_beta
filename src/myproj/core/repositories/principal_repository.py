"""Principal 仓储"""

from uuid import UUID

from myproj.core.domain.principal import (
    Principal,
    PrincipalId,
    PrincipalType,
    TrustTier,
)
from myproj.core.repositories.base import BaseRepository
from myproj.infra.db.models import PrincipalModel


class PrincipalRepository(BaseRepository[PrincipalId, Principal, PrincipalModel]):
    """Principal 仓储"""

    def _model_class(self):
        return PrincipalModel

    def _to_id_value(self, entity_id: PrincipalId) -> UUID:
        return entity_id.value

    def _get_entity_id(self, entity: Principal) -> PrincipalId:
        return entity.id

    def _to_entity(self, model: PrincipalModel) -> Principal:
        """将数据库模型转换为领域实体"""
        return Principal(
            id=PrincipalId(value=model.id),
            principal_type=PrincipalType(model.principal_type),
            display_name=model.display_name,
            email=model.email,
            phone=model.phone,
            external_id=model.external_id,
            trust_tier=TrustTier(model.trust_tier),
            disclosure_mode=model.disclosure_mode,
            disclosure_template=model.disclosure_template,
            is_active=model.is_active,
            is_verified=model.is_verified,
            avatar_url=model.avatar_url,
            timezone=model.timezone,
            locale=model.locale,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_seen_at=model.last_seen_at,
            version=model.version,
            metadata=model.meta_data or {},
        )

    def _to_model(self, entity: Principal) -> PrincipalModel:
        """将领域实体转换为数据库模型"""
        return PrincipalModel(
            id=entity.id.value,
            principal_type=entity.principal_type.value,
            display_name=entity.display_name,
            email=entity.email,
            phone=entity.phone,
            external_id=entity.external_id,
            trust_tier=entity.trust_tier.value,
            disclosure_mode=entity.disclosure_mode.value,
            disclosure_template=entity.disclosure_template,
            is_active=entity.is_active,
            is_verified=entity.is_verified,
            avatar_url=entity.avatar_url,
            timezone=entity.timezone,
            locale=entity.locale,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_seen_at=entity.last_seen_at,
            version=entity.version,
            meta_data=entity.metadata,
        )

    # Principal 专用查询方法

    def find_by_email(
        self,
        email: str,
    ) -> Principal | None:
        """按邮箱查询"""
        model = (
            self.session.query(PrincipalModel)
            .filter(PrincipalModel.email == email)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_external_id(
        self,
        external_id: str,
    ) -> Principal | None:
        """按外部ID查询"""
        model = (
            self.session.query(PrincipalModel)
            .filter(PrincipalModel.external_id == external_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_type(
        self,
        principal_type: PrincipalType,
        is_active: bool = True,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Principal]:
        """按类型查询"""
        query = self.session.query(PrincipalModel).filter(
            PrincipalModel.principal_type == principal_type.value
        )

        if is_active is not None:
            query = query.filter(PrincipalModel.is_active == is_active)

        models = query.order_by(PrincipalModel.updated_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def count_by_type(
        self,
        principal_type: PrincipalType,
        is_active: bool = True,
    ) -> int:
        """按类型统计"""
        query = self.session.query(PrincipalModel).filter(
            PrincipalModel.principal_type == principal_type.value
        )

        if is_active is not None:
            query = query.filter(PrincipalModel.is_active == is_active)

        return query.count()

    def find_trusted(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Principal]:
        """查询受信任的主体"""
        models = (
            self.session.query(PrincipalModel)
            .filter(PrincipalModel.trust_tier == TrustTier.TRUSTED.value)
            .filter(PrincipalModel.is_active == True)
            .order_by(PrincipalModel.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def search(
        self,
        query: str,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Principal]:
        """搜索主体"""
        from sqlalchemy import or_

        models = (
            self.session.query(PrincipalModel)
            .filter(
                or_(
                    PrincipalModel.display_name.ilike(f"%{query}%"),
                    PrincipalModel.email.ilike(f"%{query}%"),
                )
            )
            .filter(PrincipalModel.is_active == True)
            .order_by(PrincipalModel.display_name)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]
