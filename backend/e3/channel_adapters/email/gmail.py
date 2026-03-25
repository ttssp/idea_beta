
"""
Gmail Channel Adapter

Implements the ChannelAdapter interface for Gmail.
"""

import base64
import logging
from typing import Any

from ..base import (
    ChannelAdapter,
    ChannelMessage,
    RetryableChannelError,
    TerminalChannelError,
)

logger = logging.getLogger(__name__)


class GmailAdapter(ChannelAdapter):
    """
    Gmail适配器

    支持发送和接收Gmail邮件
    """

    def __init__(self, credentials: Any | None = None):
        """
        初始化Gmail适配器

        Args:
            credentials: Google OAuth2 credentials对象
        """
        self.credentials = credentials
        self._service = None

    @property
    def service(self):
        """获取Gmail API服务"""
        if self._service is None and self.credentials:
            try:
                from googleapiclient.discovery import build
                self._service = build('gmail', 'v1', credentials=self.credentials)
            except Exception as e:
                logger.error(f"Failed to build Gmail service: {e}")
                raise TerminalChannelError(f"Failed to initialize Gmail service: {e}")
        return self._service

    async def send_message(
        self,
        payload: dict[str, Any],
        idempotency_key: str
    ) -> dict[str, Any]:
        """
        发送邮件

        Args:
            payload: 邮件内容
                {
                    "to": "recipient@example.com",
                    "cc": ["cc@example.com"],
                    "subject": "Subject",
                    "body": "Email body",
                    "in_reply_to": "<message-id@example.com>",
                    "references": "<message-id@example.com>",
                    "thread_id": "gmail-thread-id"
                }
            idempotency_key: 幂等键

        Returns:
            {
                "external_message_id": "gmail-message-id",
                "external_thread_id": "gmail-thread-id",
                "label_ids": [...],
                "status": "sent"
            }
        """
        if not self.service:
            raise TerminalChannelError("Gmail service not initialized - no credentials")

        try:
            # 创建MIME消息
            import email.utils
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            msg = MIMEMultipart()
            msg['to'] = payload.get('to', '')
            if 'cc' in payload and payload['cc']:
                msg['cc'] = ', '.join(payload['cc'])
            msg['subject'] = payload.get('subject', '')
            msg['date'] = email.utils.formatdate()

            if 'in_reply_to' in payload:
                msg['In-Reply-To'] = payload['in_reply_to']
            if 'references' in payload:
                msg['References'] = payload['references']

            body = payload.get('body', '')
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

            # 构建发送请求
            message_body = {'raw': raw}
            if 'thread_id' in payload and payload['thread_id']:
                message_body['threadId'] = payload['thread_id']

            # 发送
            sent_msg = self.service.users().messages().send(
                userId='me',
                body=message_body
            ).execute()

            return {
                'external_message_id': sent_msg['id'],
                'external_thread_id': sent_msg.get('threadId'),
                'label_ids': sent_msg.get('labelIds', []),
                'status': 'sent'
            }

        except Exception as e:
            error_str = str(e)
            logger.error(f"Gmail send failed: {error_str}")

            # 分析错误类型
            if self._is_retryable_error(e):
                raise RetryableChannelError(f"Gmail send failed (retryable): {error_str}") from e
            else:
                raise TerminalChannelError(f"Gmail send failed (terminal): {error_str}") from e

    async def fetch_message(
        self,
        external_message_key: str
    ) -> ChannelMessage | None:
        """
        获取单条消息

        Args:
            external_message_key: Gmail消息ID

        Returns:
            ChannelMessage对象，不存在返回None
        """
        if not self.service:
            raise TerminalChannelError("Gmail service not initialized")

        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=external_message_key,
                format='full'
            ).execute()

            return self._parse_message(msg)

        except Exception as e:
            if hasattr(e, 'resp') and e.resp.status == 404:
                return None
            logger.error(f"Gmail fetch message failed: {e}")
            raise

    async def fetch_thread_messages(
        self,
        external_thread_key: str
    ) -> list[ChannelMessage]:
        """
        获取线程内所有消息

        Args:
            external_thread_key: Gmail线程ID

        Returns:
            ChannelMessage列表，按时间排序
        """
        if not self.service:
            raise TerminalChannelError("Gmail service not initialized")

        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=external_thread_key,
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date', 'Message-ID', 'In-Reply-To', 'References']
            ).execute()

            messages = []
            for msg_data in thread.get('messages', []):
                # 获取完整消息
                full_msg = self.service.users().messages().get(
                    userId='me',
                    id=msg_data['id'],
                    format='full'
                ).execute()
                parsed = self._parse_message(full_msg)
                if parsed:
                    messages.append(parsed)

            # 按时间排序
            messages.sort(key=lambda m: m.sent_at if m.sent_at else '')
            return messages

        except Exception as e:
            logger.error(f"Gmail fetch thread failed: {e}")
            raise

    async def get_external_thread_key(
        self,
        message: ChannelMessage
    ) -> str:
        """
        从消息中提取线程Key

        Args:
            message: ChannelMessage对象

        Returns:
            Gmail线程Key
        """
        # Gmail的thread_key就是thread_id
        return message.thread_key

    def validate_webhook_signature(
        self,
        payload: bytes,
        signature_header: str,
        timestamp_header: str
    ) -> bool:
        """
        验证Webhook签名

        注意：Gmail使用Cloud Pub/Sub，验证通过GCP IAM完成
        这里是简化实现

        Returns:
            验证是否通过
        """
        # 生产环境应该验证Google Pub/Sub的JWT token
        # 这里简化处理，始终返回True（开发环境）
        logger.warning("Gmail webhook signature validation is simplified in dev mode")
        return True

    def _parse_message(self, msg: dict[str, Any]) -> ChannelMessage | None:
        """
        解析Gmail API返回的消息

        Args:
            msg: Gmail API消息对象

        Returns:
            ChannelMessage对象
        """
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])

        def get_header(name: str) -> str | None:
            for h in headers:
                if h.get('name', '').lower() == name.lower():
                    return h.get('value')
            return None

        # 提取body
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    body_data = part.get('body', {}).get('data')
                    if body_data:
                        try:
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                        except Exception:
                            pass
                    break
        elif 'body' in payload:
            body_data = payload['body'].get('data')
            if body_data:
                try:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                except Exception:
                    pass

        # 解析发送者
        sender_email = get_header('From') or ''
        sender = {'email': sender_email}

        # 解析接收者
        to_email = get_header('To') or ''
        recipients = [{'email': to_email}] if to_email else []

        # 构建ChannelMessage
        return ChannelMessage(
            id=msg.get('id', ''),
            thread_key=msg.get('threadId', msg.get('id', '')),
            sender=sender,
            recipients=recipients,
            subject=get_header('Subject') or '',
            body=body,
            sent_at=get_header('Date') or '',
            metadata={
                'label_ids': msg.get('labelIds', []),
                'history_id': msg.get('historyId')
            },
            in_reply_to=get_header('In-Reply-To'),
            references=get_header('References')
        )

    def _is_retryable_error(self, error: Exception) -> bool:
        """
        判断错误是否可重试

        Returns:
            是否可以重试
        """
        error_str = str(error).lower()

        # 网络错误、超时、5xx错误可重试
        retryable_keywords = [
            'timeout',
            'timed out',
            'connection',
            'server error',
            '500',
            '502',
            '503',
            '504',
            'service unavailable',
            'rate limit',
            '429'
        ]

        for keyword in retryable_keywords:
            if keyword in error_str:
                return True

        return False

