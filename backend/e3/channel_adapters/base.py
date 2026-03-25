
"""
Channel Adapter Base Interface

Defines the unified interface that all channel adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChannelMessage(BaseModel):
    """统一的通道消息格式"""
    id: str = Field(..., description="外部消息ID")
    thread_key: str = Field(..., description="外部线程Key")
    sender: Dict[str, str] = Field(..., description="发送者信息 {'email': ...}")
    recipients: List[Dict[str, str]] = Field(..., description="接收者列表")
    subject: Optional[str] = Field(None, description="主题")
    body: str = Field(..., description="消息正文")
    sent_at: str = Field(..., description="发送时间（ISO格式）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    in_reply_to: Optional[str] = Field(None, description="回复的消息ID")
    references: Optional[str] = Field(None, description="引用链")


class ChannelAdapter(ABC):
    """
    统一的Channel Adapter接口

    所有外部渠道适配器都必须实现此接口。
    """

    @abstractmethod
    async def send_message(
        self,
        payload: Dict[str, Any],
        idempotency_key: str
    ) -&gt; Dict[str, Any]:
        """
        发送消息

        Args:
            payload: 消息内容，结构取决于具体渠道
            idempotency_key: 幂等键

        Returns:
            包含external_message_id和external_thread_id的字典

        Raises:
            RetryableChannelError: 可重试的错误（网络超时等）
            TerminalChannelError: 不可重试的错误（认证失败等）
        """
        pass

    @abstractmethod
    async def fetch_message(
        self,
        external_message_key: str
    ) -&gt; Optional[ChannelMessage]:
        """
        获取单条消息

        Args:
            external_message_key: 外部消息Key

        Returns:
            ChannelMessage对象，不存在返回None
        """
        pass

    @abstractmethod
    async def fetch_thread_messages(
        self,
        external_thread_key: str
    ) -&gt; List[ChannelMessage]:
        """
        获取线程内所有消息

        Args:
            external_thread_key: 外部线程Key

        Returns:
            ChannelMessage列表，按时间排序
        """
        pass

    @abstractmethod
    async def get_external_thread_key(
        self,
        message: ChannelMessage
    ) -&gt; str:
        """
        从消息中提取线程Key

        Args:
            message: ChannelMessage对象

        Returns:
            外部线程Key
        """
        pass

    @abstractmethod
    def validate_webhook_signature(
        self,
        payload: bytes,
        signature_header: str,
        timestamp_header: str
    ) -&gt; bool:
        """
        验证Webhook签名

        Args:
            payload: 请求体原始字节
            signature_header: 签名请求头
            timestamp_header: 时间戳请求头

        Returns:
            验证是否通过
        """
        pass


class ChannelError(Exception):
    """Channel异常基类"""
    pass


class RetryableChannelError(ChannelError):
    """可重试的Channel异常"""
    pass


class TerminalChannelError(ChannelError):
    """不可重试的Channel异常"""
    pass

