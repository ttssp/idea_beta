"""数据库ORM模型"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from myproj.infra.db.session import Base

# ============================================
# Thread 模型
# ============================================

class ThreadModel(Base):
    """Thread 数据库模型"""

    __tablename__ = "threads"

    # 标识
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # 目标
    objective_title = Column(String(200), nullable=False)
    objective_description = Column(Text, nullable=True)
    objective_due_at = Column(DateTime(timezone=True), nullable=True)

    # 状态
    status = Column(String(50), nullable=False, index=True, default="new")
    risk_level = Column(String(50), nullable=False, default="low")

    # 委托配置
    delegation_profile_name = Column(String(100), nullable=True)
    delegation_level = Column(String(50), nullable=True, default="observe_only")
    delegation_max_actions_per_hour = Column(Integer, default=10)
    delegation_max_messages_per_thread = Column(Integer, default=50)
    delegation_max_consecutive_touches = Column(Integer, default=3)
    delegation_allowed_actions = Column(JSON, default=list)
    delegation_escalation_rules = Column(JSON, default=dict)

    # 责任人与参与者
    owner_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    responsible_principal_id = Column(PGUUID(as_uuid=True), nullable=True, index=True)
    participant_ids = Column(JSON, default=list)

    # 摘要与元数据
    summary = Column(String(500), nullable=True)
    current_step = Column(String(500), nullable=True)
    tags = Column(JSON, default=list)

    # 时间戳
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_escalated_at = Column(DateTime(timezone=True), nullable=True)
    last_escalation_reason = Column(Text, nullable=True)

    # 乐观锁
    version = Column(Integer, nullable=False, default=1)

    # 上下文数据
    context = Column(JSON, default=dict)

    # 关系
    messages = relationship("MessageModel", back_populates="thread", cascade="all, delete-orphan")
    events = relationship("ThreadEventModel", back_populates="thread", cascade="all, delete-orphan")
    external_bindings = relationship("ExternalBindingModel", back_populates="thread", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index("idx_thread_owner_status", "owner_id", "status"),
        Index("idx_thread_status_updated", "status", "updated_at"),
        Index("idx_thread_risk_level", "risk_level"),
    )


# ============================================
# Principal 模型
# ============================================

class PrincipalModel(Base):
    """Principal 数据库模型"""

    __tablename__ = "principals"

    # 标识
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # 核心属性
    principal_type = Column(String(50), nullable=False, index=True)
    display_name = Column(String(200), nullable=False)

    # 联系方式
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    external_id = Column(String(255), nullable=True, index=True)

    # 信任与披露
    trust_tier = Column(String(50), nullable=False, default="unknown")
    disclosure_mode = Column(String(50), nullable=False, default="semi")
    disclosure_template = Column(String(500), nullable=True)

    # 元数据
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(100), nullable=True)
    locale = Column(String(20), nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)

    # 乐观锁
    version = Column(Integer, nullable=False, default=1)

    # 扩展数据
    meta_data = Column(JSON, default=dict, name="metadata")

    # 关系
    relationships_from = relationship(
        "RelationshipModel",
        foreign_keys="RelationshipModel.from_principal_id",
        back_populates="from_principal",
        cascade="all, delete-orphan",
    )
    relationships_to = relationship(
        "RelationshipModel",
        foreign_keys="RelationshipModel.to_principal_id",
        back_populates="to_principal",
        cascade="all, delete-orphan",
    )

    # 索引
    __table_args__ = (
        Index("idx_principal_type", "principal_type"),
        Index("idx_principal_email", "email"),
        Index("idx_principal_external_id", "external_id"),
    )


# ============================================
# Relationship 模型
# ============================================

class RelationshipModel(Base):
    """Relationship 数据库模型"""

    __tablename__ = "relationships"

    # 标识
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # 关系双方
    from_principal_id = Column(PGUUID(as_uuid=True), ForeignKey("principals.id"), nullable=False, index=True)
    to_principal_id = Column(PGUUID(as_uuid=True), ForeignKey("principals.id"), nullable=False, index=True)

    # 关系语义
    relationship_class = Column(String(50), nullable=False, index=True)
    sensitivity = Column(String(50), nullable=False, default="medium")

    # 委托配置
    default_delegation_profile = Column(JSON, nullable=True)
    custom_delegation_profile = Column(JSON, nullable=True)

    # 关系元数据
    alias = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)

    # 状态
    is_active = Column(Boolean, nullable=False, default=True)
    is_favorite = Column(Boolean, nullable=False, default=False)

    # 交互历史
    first_interaction_at = Column(DateTime(timezone=True), nullable=True)
    last_interaction_at = Column(DateTime(timezone=True), nullable=True)
    interaction_count = Column(Integer, nullable=False, default=0)

    # 时间戳
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # 乐观锁
    version = Column(Integer, nullable=False, default=1)

    # 扩展数据
    meta_data = Column(JSON, default=dict, name="metadata")

    # 关系
    from_principal = relationship(
        "PrincipalModel",
        foreign_keys=[from_principal_id],
        back_populates="relationships_from",
    )
    to_principal = relationship(
        "PrincipalModel",
        foreign_keys=[to_principal_id],
        back_populates="relationships_to",
    )

    # 索引
    __table_args__ = (
        Index("idx_relationship_pair", "from_principal_id", "to_principal_id", unique=True),
        Index("idx_relationship_class", "relationship_class"),
        Index("idx_relationship_sensitivity", "sensitivity"),
    )


# ============================================
# Message 模型
# ============================================

class MessageModel(Base):
    """Message 数据库模型"""

    __tablename__ = "messages"

    # 标识
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # 所属线程
    thread_id = Column(PGUUID(as_uuid=True), ForeignKey("threads.id"), nullable=False, index=True)

    # 创作与发送信息
    authored_mode = Column(String(100), nullable=False, index=True)
    channel = Column(String(50), nullable=False, default="internal")

    # 主体信息
    sender_principal_id = Column(PGUUID(as_uuid=True), nullable=False)
    author_principal_id = Column(PGUUID(as_uuid=True), nullable=True)
    approver_principal_id = Column(PGUUID(as_uuid=True), nullable=True)

    # 内容
    subject = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)
    content_markdown = Column(Text, nullable=True)

    # 引用与回复
    parent_message_id = Column(PGUUID(as_uuid=True), nullable=True)
    reply_to_external_id = Column(String(255), nullable=True)
    external_message_id = Column(String(255), nullable=True, index=True)

    # 审批关联
    approval_request_id = Column(PGUUID(as_uuid=True), nullable=True)

    # 身份披露
    disclosure = Column(JSON, nullable=True)

    # 附件
    attachments = Column(JSON, default=list)

    # 元数据
    is_draft = Column(Boolean, nullable=False, default=True)
    is_sent = Column(Boolean, nullable=False, default=False)
    is_read = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # 发送状态
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    delivery_status = Column(String(50), nullable=True)
    delivery_error = Column(Text, nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # 乐观锁
    version = Column(Integer, nullable=False, default=1)

    # 扩展数据
    meta_data = Column(JSON, default=dict, name="metadata")

    # 关系
    thread = relationship("ThreadModel", back_populates="messages")

    # 索引
    __table_args__ = (
        Index("idx_message_thread", "thread_id"),
        Index("idx_message_thread_created", "thread_id", "created_at"),
        Index("idx_message_authored_mode", "authored_mode"),
        Index("idx_message_external_id", "external_message_id"),
    )


# ============================================
# ThreadEvent 模型
# ============================================

class ThreadEventModel(Base):
    """ThreadEvent 数据库模型 - append-only"""

    __tablename__ = "thread_events"

    # 标识
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # 所属线程
    thread_id = Column(PGUUID(as_uuid=True), ForeignKey("threads.id"), nullable=False, index=True)

    # 事件元数据
    event_type = Column(String(100), nullable=False, index=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)

    # 事件顺序（用于保证顺序）
    sequence_number = Column(Integer, nullable=False, index=True)

    # 执行者
    actor_principal_id = Column(PGUUID(as_uuid=True), nullable=True)
    actor_type = Column(String(50), nullable=True)

    # 因果关系
    causal_event_id = Column(PGUUID(as_uuid=True), nullable=True)
    causal_ref = Column(String(255), nullable=True)

    # 事件内容
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # 结构化数据
    payload = Column(JSON, default=dict)

    # 状态快照（可选，用于回放）
    thread_status_before = Column(String(50), nullable=True)
    thread_status_after = Column(String(50), nullable=True)

    # 幂等性
    idempotency_key = Column(String(255), nullable=True, index=True, unique=True)

    # 元数据
    is_replayed = Column(Boolean, nullable=False, default=False)
    is_visible = Column(Boolean, nullable=False, default=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # 关系
    thread = relationship("ThreadModel", back_populates="events")

    # 索引
    __table_args__ = (
        Index("idx_event_thread_sequence", "thread_id", "sequence_number", unique=True),
        Index("idx_event_thread_type", "thread_id", "event_type"),
        Index("idx_event_occurred_at", "occurred_at"),
        Index("idx_event_idempotency", "idempotency_key"),
    )


# ============================================
# ExternalBinding 模型
# ============================================

class ExternalBindingModel(Base):
    """ExternalBinding 数据库模型"""

    __tablename__ = "external_bindings"

    # 标识
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # 所属线程
    thread_id = Column(PGUUID(as_uuid=True), ForeignKey("threads.id"), nullable=False, index=True)

    # 渠道信息
    channel = Column(String(50), nullable=False, index=True)
    channel_account_id = Column(String(255), nullable=True)

    # 外部线程/消息标识
    external_thread_key = Column(String(500), nullable=True, index=True)
    external_message_key = Column(String(500), nullable=True, index=True)

    # 关联的消息
    message_id = Column(PGUUID(as_uuid=True), nullable=True)

    # 同步状态
    sync_state = Column(String(50), nullable=False, default="pending", index=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    sync_error = Column(Text, nullable=True)

    # 方向
    is_inbound = Column(Boolean, nullable=False, default=False)
    is_outbound = Column(Boolean, nullable=False, default=True)

    # 元数据
    is_active = Column(Boolean, nullable=False, default=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    sync_direction = Column(String(50), nullable=False, default="bidirectional")

    # 外部数据快照
    external_subject = Column(String(500), nullable=True)
    external_sender = Column(String(500), nullable=True)
    external_recipients = Column(JSON, default=list)
    external_meta_data = Column(JSON, default=dict, name="external_metadata")

    # 时间戳
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    external_created_at = Column(DateTime(timezone=True), nullable=True)
    external_updated_at = Column(DateTime(timezone=True), nullable=True)

    # 乐观锁
    version = Column(Integer, nullable=False, default=1)

    # 扩展数据
    meta_data = Column(JSON, default=dict, name="metadata")

    # 关系
    thread = relationship("ThreadModel", back_populates="external_bindings")

    # 索引
    __table_args__ = (
        Index("idx_binding_thread", "thread_id"),
        Index("idx_binding_channel_thread", "channel", "external_thread_key"),
        Index("idx_binding_channel_message", "channel", "external_message_key"),
        Index("idx_binding_sync_state", "sync_state"),
    )
