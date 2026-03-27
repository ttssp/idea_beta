"""Relationship 仓储"""

from uuid import UUID

from myproj.core.domain.principal import PrincipalId
from myproj.core.domain.relationship import (
    Relationship,
    RelationshipClass,
    RelationshipId,
    SensitivityLevel,
)
from myproj.core.repositories.base import BaseRepository
from myproj.infra.db.models import RelationshipModel


class RelationshipRepository(BaseRepository[RelationshipId, Relationship, RelationshipModel]):
    """Relationship 仓储"""

    def _model_class(self):
        return RelationshipModel

    def _to_id_value(self, entity_id: RelationshipId) -> UUID:
        return entity_id.value

    def _get_entity_id(self, entity: Relationship) -> RelationshipId:
        return entity.id

    def _to_entity(self, model: RelationshipModel) -> Relationship:
        """将数据库模型转换为领域实体"""
        return Relationship(
            id=RelationshipId(value=model.id),
            from_principal_id=PrincipalId(value=model.from_principal_id),
            to_principal_id=PrincipalId(value=model.to_principal_id),
            relationship_class=RelationshipClass(model.relationship_class),
            sensitivity=SensitivityLevel(model.sensitivity),
            default_delegation_profile=model.default_delegation_profile,
            custom_delegation_profile=model.custom_delegation_profile,
            alias=model.alias,
            notes=model.notes,
            tags=model.tags or [],
            is_active=model.is_active,
            is_favorite=model.is_favorite,
            first_interaction_at=model.first_interaction_at,
            last_interaction_at=model.last_interaction_at,
            interaction_count=model.interaction_count,
            created_at=model.created_at,
            updated_at=model.updated_at,
            version=model.version,
            metadata=model.meta_data or {},
        )

    def _to_model(self, entity: Relationship) -> RelationshipModel:
        """将领域实体转换为数据库模型"""
        return RelationshipModel(
            id=entity.id.value,
            from_principal_id=entity.from_principal_id.value,
            to_principal_id=entity.to_principal_id.value,
            relationship_class=entity.relationship_class.value,
            sensitivity=entity.sensitivity.value,
            default_delegation_profile=entity.default_delegation_profile,
            custom_delegation_profile=entity.custom_delegation_profile,
            alias=entity.alias,
            notes=entity.notes,
            tags=entity.tags,
            is_active=entity.is_active,
            is_favorite=entity.is_favorite,
            first_interaction_at=entity.first_interaction_at,
            last_interaction_at=entity.last_interaction_at,
            interaction_count=entity.interaction_count,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            version=entity.version,
            meta_data=entity.metadata,
        )

    # Relationship 专用查询方法

    def find_by_principal(
        self,
        principal_id: PrincipalId,
        relationship_class: RelationshipClass | None = None,
        is_active: bool = True,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Relationship]:
        """按主体查询关系"""
        from sqlalchemy import or_

        query = self.session.query(RelationshipModel).filter(
            or_(
                RelationshipModel.from_principal_id == principal_id.value,
                RelationshipModel.to_principal_id == principal_id.value,
            )
        )

        if relationship_class:
            query = query.filter(RelationshipModel.relationship_class == relationship_class.value)

        if is_active is not None:
            query = query.filter(RelationshipModel.is_active == is_active)

        models = query.order_by(RelationshipModel.updated_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def find_by_class(
        self,
        relationship_class: RelationshipClass,
        is_active: bool = True,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Relationship]:
        """按关系类查询"""
        query = self.session.query(RelationshipModel).filter(
            RelationshipModel.relationship_class == relationship_class.value
        )

        if is_active is not None:
            query = query.filter(RelationshipModel.is_active == is_active)

        models = query.order_by(RelationshipModel.updated_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def find_sensitive(
        self,
        principal_id: PrincipalId | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Relationship]:
        """查询敏感关系"""
        from sqlalchemy import or_

        query = self.session.query(RelationshipModel).filter(
            RelationshipModel.sensitivity.in_(
                [SensitivityLevel.HIGH.value, SensitivityLevel.CRITICAL.value]
            )
        ).filter(RelationshipModel.is_active == True)

        if principal_id:
            query = query.filter(
                or_(
                    RelationshipModel.from_principal_id == principal_id.value,
                    RelationshipModel.to_principal_id == principal_id.value,
                )
            )

        models = query.order_by(RelationshipModel.updated_at.desc()).offset(offset).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def find_between(
        self,
        from_principal_id: PrincipalId,
        to_principal_id: PrincipalId,
    ) -> Relationship | None:
        """查询两个主体之间的关系"""
        from sqlalchemy import or_

        model = (
            self.session.query(RelationshipModel)
            .filter(
                or_(
                    (RelationshipModel.from_principal_id == from_principal_id.value)
                    & (RelationshipModel.to_principal_id == to_principal_id.value),
                    (RelationshipModel.from_principal_id == to_principal_id.value)
                    & (RelationshipModel.to_principal_id == from_principal_id.value),
                )
            )
            .first()
        )
        return self._to_entity(model) if model else None

    def find_favorites(
        self,
        principal_id: PrincipalId,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Relationship]:
        """查询收藏的关系"""
        from sqlalchemy import or_

        models = (
            self.session.query(RelationshipModel)
            .filter(
                or_(
                    RelationshipModel.from_principal_id == principal_id.value,
                    RelationshipModel.to_principal_id == principal_id.value,
                )
            )
            .filter(RelationshipModel.is_favorite == True)
            .filter(RelationshipModel.is_active == True)
            .order_by(RelationshipModel.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]
