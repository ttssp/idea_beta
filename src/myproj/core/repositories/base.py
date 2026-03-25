"""仓储基类"""

from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.orm import Session


class BaseRepository[EntityId, Entity, Model](ABC):
    """仓储基类"""

    def __init__(self, session: Session):
        self.session = session

    @abstractmethod
    def _to_entity(self, model: Model) -> Entity:
        """将数据库模型转换为领域实体"""
        pass

    @abstractmethod
    def _to_model(self, entity: Entity) -> Model:
        """将领域实体转换为数据库模型"""
        pass

    def get(self, entity_id: EntityId) -> Entity | None:
        """根据ID获取实体"""
        model = self.session.query(self._model_class()).get(self._to_id_value(entity_id))
        if not model:
            return None
        return self._to_entity(model)

    def get_by_uuid(self, uuid: UUID) -> Entity | None:
        """根据UUID获取实体"""
        model = self.session.query(self._model_class()).get(uuid)
        if not model:
            return None
        return self._to_entity(model)

    def list(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Entity]:
        """列出实体"""
        models = (
            self.session.query(self._model_class())
            .order_by(self._model_class().created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def count(self) -> int:
        """统计实体数量"""
        return self.session.query(self._model_class()).count()

    def save(self, entity: Entity) -> Entity:
        """保存实体"""
        # 检查是否已存在
        existing = self.get(self._get_entity_id(entity))

        if existing:
            # 更新 - merge 返回值必须接住，这才是 attached 实例
            model = self._to_model(entity)
            model = self.session.merge(model)
        else:
            # 新建
            model = self._to_model(entity)
            self.session.add(model)

        self.session.flush()
        self.session.refresh(model)
        return self._to_entity(model)

    def delete(self, entity_id: EntityId) -> bool:
        """删除实体"""
        model = self.session.query(self._model_class()).get(self._to_id_value(entity_id))
        if not model:
            return False
        self.session.delete(model)
        self.session.flush()
        return True

    @abstractmethod
    def _model_class(self):
        """获取数据库模型类"""
        pass

    @abstractmethod
    def _to_id_value(self, entity_id: EntityId):
        """将实体ID转换为数据库ID值"""
        pass

    @abstractmethod
    def _get_entity_id(self, entity: Entity) -> EntityId:
        """从实体获取ID"""
        pass
