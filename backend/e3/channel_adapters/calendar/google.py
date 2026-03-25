
"""
Google Calendar Channel Adapter

Implements the ChannelAdapter interface for Google Calendar.
"""

from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timedelta

from ..base import (
    ChannelAdapter,
    ChannelMessage,
    ChannelError,
    RetryableChannelError,
    TerminalChannelError
)
from ..circuit_breaker import (
    calendar_circuit,
    calendar_adapter_exception_handler
)

logger = logging.getLogger(__name__)


class GoogleCalendarAdapter(ChannelAdapter):
    """
    Google Calendar适配器

    支持创建、更新、查询日历事件
    """

    def __init__(self, credentials: Optional[Any] = None):
        """
        初始化Google Calendar适配器

        Args:
            credentials: Google OAuth2 credentials对象
        """
        self.credentials = credentials
        self._service = None

    @property
    def service(self):
        """获取Calendar API服务"""
        if self._service is None and self.credentials:
            try:
                from googleapiclient.discovery import build
                self._service = build('calendar', 'v3', credentials=self.credentials)
            except Exception as e:
                logger.error(f"Failed to build Calendar service: {e}")
                raise TerminalChannelError(f"Failed to initialize Calendar service: {e}")
        return self._service

    async def send_message(
        self,
        payload: Dict[str, Any],
        idempotency_key: str
    ) -> Dict[str, Any]:
        """
        发送消息（对于Calendar，这意味着创建/更新事件）

        Args:
            payload: 事件内容
                {
                    "action": "create|update|cancel",
                    "calendar_id": "primary",
                    "event_id": "event-id",  # 用于update/cancel
                    "event": {
                        "summary": "Event title",
                        "description": "Event description",
                        "start": {"dateTime": "2024-01-01T10:00:00Z"},
                        "end": {"dateTime": "2024-01-01T11:00:00Z"},
                        "attendees": [{"email": "attendee@example.com"}],
                        "conferenceData": {...}  # Google Meet
                    }
                }
            idempotency_key: 幂等键

        Returns:
            创建/更新的事件信息
        """
        if not self.service:
            raise TerminalChannelError("Calendar service not initialized - no credentials")

        try:
            action = payload.get('action', 'create')
            calendar_id = payload.get('calendar_id', 'primary')
            event_data = payload.get('event', {})

            # 使用iCalUID作为幂等键
            if 'iCalUID' not in event_data:
                event_data['iCalUID'] = f"{idempotency_key}@our-system.local"

            if action == 'create':
                # 先检查是否已存在（通过iCalUID）
                existing_event = await self._find_event_by_icaluid(
                    calendar_id, event_data['iCalUID']
                )
                if existing_event:
                    logger.info(f"Event already exists, returning existing: {existing_event['id']}")
                    return {
                        'external_event_id': existing_event['id'],
                        'external_calendar_id': calendar_id,
                        'ical_uid': event_data['iCalUID'],
                        'status': 'already_exists',
                        'event': existing_event
                    }

                # 创建事件
                conference_data_version = 1 if 'conferenceData' in event_data else 0
                event = self.service.events().insert(
                    calendarId=calendar_id,
                    body=event_data,
                    conferenceDataVersion=conference_data_version
                ).execute()

                return {
                    'external_event_id': event['id'],
                    'external_calendar_id': calendar_id,
                    'ical_uid': event.get('iCalUID'),
                    'html_link': event.get('htmlLink'),
                    'status': 'created',
                    'event': event
                }

            elif action == 'update':
                event_id = payload.get('event_id')
                if not event_id:
                    raise ValueError("event_id is required for update")

                event = self.service.events().patch(
                    calendarId=calendar_id,
                    eventId=event_id,
                    body=event_data
                ).execute()

                return {
                    'external_event_id': event['id'],
                    'external_calendar_id': calendar_id,
                    'status': 'updated',
                    'event': event
                }

            elif action == 'cancel':
                event_id = payload.get('event_id')
                if not event_id:
                    raise ValueError("event_id is required for cancel")

                self.service.events().delete(
                    calendarId=calendar_id,
                    eventId=event_id
                ).execute()

                return {
                    'external_event_id': event_id,
                    'external_calendar_id': calendar_id,
                    'status': 'cancelled'
                }

            else:
                raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Google Calendar operation failed: {e}")

            if self._is_retryable_error(e):
                raise RetryableChannelError(f"Calendar operation failed (retryable): {e}") from e
            else:
                raise TerminalChannelError(f"Calendar operation failed (terminal): {e}") from e

    async def fetch_message(
        self,
        external_message_key: str
    ) -> Optional[ChannelMessage]:
        """
        获取单个事件

        Args:
            external_message_key: Calendar事件ID，格式为 "calendar_id:event_id"

        Returns:
            ChannelMessage对象
        """
        if not self.service:
            raise TerminalChannelError("Calendar service not initialized")

        try:
            if ':' in external_message_key:
                calendar_id, event_id = external_message_key.split(':', 1)
            else:
                calendar_id = 'primary'
                event_id = external_message_key

            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            return self._event_to_channel_message(event, calendar_id)

        except Exception as e:
            if hasattr(e, 'resp') and e.resp.status == 404:
                return None
            logger.error(f"Fetch calendar event failed: {e}")
            raise

    async def fetch_thread_messages(
        self,
        external_thread_key: str
    ) -> List[ChannelMessage]:
        """
        获取线程内所有消息（对于Calendar，这是单个事件）

        Args:
            external_thread_key: Calendar事件ID

        Returns:
            包含单个ChannelMessage的列表
        """
        msg = await self.fetch_message(external_thread_key)
        return [msg] if msg else []

    async def get_external_thread_key(
        self,
        message: ChannelMessage
    ) -> str:
        """
        从消息中提取线程Key

        Args:
            message: ChannelMessage对象

        Returns:
            Calendar事件Key
        """
        return message.thread_key

    def validate_webhook_signature(
        self,
        payload: bytes,
        signature_header: str,
        timestamp_header: str
    ) -> bool:
        """
        验证Webhook签名

        Returns:
            验证是否通过
        """
        logger.warning("Calendar webhook signature validation is simplified in dev mode")
        return True

    async def get_free_busy(
        self,
        calendar_ids: List[str],
        time_min: datetime,
        time_max: datetime,
        time_zone: str = 'UTC'
    ) -> Dict[str, Any]:
        """
        查询忙闲时间

        Args:
            calendar_ids: 日历ID列表
            time_min: 开始时间
            time_max: 结束时间
            time_zone: 时区

        Returns:
            忙闲信息
        """
        if not self.service:
            raise TerminalChannelError("Calendar service not initialized")

        body = {
            "timeMin": time_min.isoformat() + 'Z',
            "timeMax": time_max.isoformat() + 'Z',
            "timeZone": time_zone,
            "items": [{"id": cid} for cid in calendar_ids]
        }

        response = self.service.freebusy().query(body=body).execute()
        return response

    async def list_events(
        self,
        calendar_id: str = 'primary',
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        列出事件

        Args:
            calendar_id: 日历ID
            time_min: 最小时间（默认现在）
            time_max: 最大时间（默认30天后）
            max_results: 最大数量

        Returns:
            事件列表
        """
        if not self.service:
            raise TerminalChannelError("Calendar service not initialized")

        if time_min is None:
            time_min = datetime.utcnow()
        if time_max is None:
            time_max = time_min + timedelta(days=30)

        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=time_min.isoformat() + 'Z',
            timeMax=time_max.isoformat() + 'Z',
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return events_result.get('items', [])

    def _event_to_channel_message(
        self,
        event: Dict[str, Any],
        calendar_id: str
    ) -> ChannelMessage:
        """将Calendar事件转换为ChannelMessage"""
        start = event.get('start', {})
        end = event.get('end', {})
        attendees = event.get('attendees', [])

        sender_email = event.get('creator', {}).get('email', '')
        recipient_emails = [a.get('email', '') for a in attendees if a.get('email')]

        start_time = start.get('dateTime', start.get('date', ''))
        end_time = end.get('dateTime', end.get('date', ''))

        body = (
            f"Calendar Event: {event.get('summary', '')}\n"
            f"Start: {start_time}\n"
            f"End: {end_time}\n"
            f"Description: {event.get('description', '')}"
        )

        return ChannelMessage(
            id=f"{calendar_id}:{event.get('id', '')}",
            thread_key=event.get('iCalUID', event.get('id', '')),
            sender={'email': sender_email},
            recipients=[{'email': e} for e in recipient_emails],
            subject=event.get('summary', ''),
            body=body,
            sent_at=event.get('created', ''),
            metadata={
                'calendar_id': calendar_id,
                'event_id': event.get('id'),
                'ical_uid': event.get('iCalUID'),
                'html_link': event.get('htmlLink'),
                'status': event.get('status')
            }
        )

    async def _find_event_by_icaluid(
        self,
        calendar_id: str,
        ical_uid: str
    ) -> Optional[Dict[str, Any]]:
        """通过iCalUID查找事件（用于幂等）"""
        # 简化实现：列出最近事件并查找
        # 生产环境应该使用syncToken或watch机制
        events = await self.list_events(
            calendar_id=calendar_id,
            max_results=100
        )

        for event in events:
            if event.get('iCalUID') == ical_uid:
                return event

        return None

    def _is_retryable_error(self, error: Exception) -> bool:
        """判断错误是否可重试"""
        error_str = str(error).lower()

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

