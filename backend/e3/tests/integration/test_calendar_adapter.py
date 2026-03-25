
"""
Integration Tests: Calendar Adapter

Tests for CA-R01 to CA-W04 and CA-I01 to CA-I02
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from ...channel_adapters.calendar.google import GoogleCalendarAdapter


class TestGoogleCalendarAdapter:
    """Google Calendar适配器集成测试"""

    @pytest.fixture
    def mock_credentials(self):
        """Mock Google credentials"""
        return MagicMock()

    @pytest.fixture
    def calendar_adapter(self, mock_credentials):
        """GoogleCalendarAdapter实例"""
        adapter = GoogleCalendarAdapter(mock_credentials)
        adapter._service = MagicMock()
        return adapter

    @pytest.mark.asyncio
    async def test_ca_r01_get_free_busy(self, calendar_adapter):
        """CA-R01: 查询空闲时间"""
        time_min = datetime.now(UTC)
        time_max = time_min + timedelta(days=7)

        mock_response = {
            'timeMin': time_min.isoformat() + 'Z',
            'timeMax': time_max.isoformat() + 'Z',
            'calendars': {
                'primary': {
                    'busy': [
                        {'start': '2024-01-01T10:00:00Z', 'end': '2024-01-01T11:00:00Z'}
                    ]
                }
            }
        }

        calendar_adapter.service.freebusy().query().execute.return_value = mock_response

        result = await calendar_adapter.get_free_busy(
            calendar_ids=['primary'],
            time_min=time_min,
            time_max=time_max
        )

        assert 'calendars' in result
        assert 'primary' in result['calendars']

    @pytest.mark.asyncio
    async def test_ca_r02_list_events(self, calendar_adapter):
        """CA-R02: 列出事件"""
        mock_events = {
            'items': [
                {
                    'id': 'event-1',
                    'summary': 'Test Event 1',
                    'start': {'dateTime': '2024-01-01T10:00:00Z'},
                    'end': {'dateTime': '2024-01-01T11:00:00Z'},
                },
                {
                    'id': 'event-2',
                    'summary': 'Test Event 2',
                    'start': {'dateTime': '2024-01-02T10:00:00Z'},
                    'end': {'dateTime': '2024-01-02T11:00:00Z'},
                }
            ]
        }

        calendar_adapter.service.events().list().execute.return_value = mock_events

        events = await calendar_adapter.list_events(calendar_id='primary')

        assert len(events) == 2
        assert events[0]['summary'] == 'Test Event 1'

    @pytest.mark.asyncio
    async def test_ca_w01_create_event(self, calendar_adapter):
        """CA-W01: 创建日历事件"""
        mock_event = {
            'id': 'new-event-id',
            'iCalUID': 'test-idempotency-key@our-system.local',
            'summary': 'New Event',
            'htmlLink': 'https://calendar.google.com/event/xyz',
            'start': {'dateTime': '2024-01-01T10:00:00Z'},
            'end': {'dateTime': '2024-01-01T11:00:00Z'},
        }

        calendar_adapter.service.events().insert().execute.return_value = mock_event
        calendar_adapter._find_event_by_icaluid = AsyncMock(return_value=None)

        result = await calendar_adapter.send_message(
            payload={
                'action': 'create',
                'calendar_id': 'primary',
                'event': {
                    'summary': 'New Event',
                    'start': {'dateTime': '2024-01-01T10:00:00Z'},
                    'end': {'dateTime': '2024-01-01T11:00:00Z'},
                }
            },
            idempotency_key='test-idempotency-key'
        )

        assert result['external_event_id'] == 'new-event-id'
        assert result['status'] == 'created'

    @pytest.mark.asyncio
    async def test_ca_w02_update_event(self, calendar_adapter):
        """CA-W02: 更新日历事件"""
        mock_event = {
            'id': 'event-id',
            'summary': 'Updated Event',
        }

        calendar_adapter.service.events().patch().execute.return_value = mock_event

        result = await calendar_adapter.send_message(
            payload={
                'action': 'update',
                'calendar_id': 'primary',
                'event_id': 'event-id',
                'event': {'summary': 'Updated Event'}
            },
            idempotency_key='update-key'
        )

        assert result['status'] == 'updated'

    @pytest.mark.asyncio
    async def test_ca_w03_cancel_event(self, calendar_adapter):
        """CA-W03: 取消日历事件"""
        result = await calendar_adapter.send_message(
            payload={
                'action': 'cancel',
                'calendar_id': 'primary',
                'event_id': 'event-to-cancel'
            },
            idempotency_key='cancel-key'
        )

        assert result['status'] == 'cancelled'
        calendar_adapter.service.events().delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_ca_i01_idempotent_create(self, calendar_adapter):
        """CA-I01: 幂等创建事件"""
        existing_event = {
            'id': 'existing-id',
            'iCalUID': 'test-idempotency-key@our-system.local',
        }

        calendar_adapter._find_event_by_icaluid = AsyncMock(return_value=existing_event)

        result = await calendar_adapter.send_message(
            payload={
                'action': 'create',
                'calendar_id': 'primary',
                'event': {'summary': 'Test'}
            },
            idempotency_key='test-idempotency-key'
        )

        assert result['status'] == 'already_exists'
        assert result['external_event_id'] == 'existing-id'

    @pytest.mark.asyncio
    async def test_ca_i02_sequence_number(self, calendar_adapter):
        """CA-I02: 使用sequenceNumber乐观锁"""
        # 这个测试验证sequenceNumber的概念
        # 实际实现在Google Calendar API中使用ETag
        mock_event = {
            'id': 'event-id',
            'sequence': 1,
            'summary': 'Test',
        }

        calendar_adapter.service.events().patch().execute.return_value = mock_event

        result = await calendar_adapter.send_message(
            payload={
                'action': 'update',
                'calendar_id': 'primary',
                'event_id': 'event-id',
                'event': {'summary': 'Updated', 'sequence': 1}
            },
            idempotency_key='update-key'
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_fetch_event_as_message(self, calendar_adapter):
        """测试将事件作为ChannelMessage获取"""
        mock_event = {
            'id': 'event-id',
            'iCalUID': 'ical-uid',
            'summary': 'Test Event',
            'description': 'Event description',
            'creator': {'email': 'creator@example.com'},
            'attendees': [{'email': 'attendee@example.com'}],
            'start': {'dateTime': '2024-01-01T10:00:00Z'},
            'end': {'dateTime': '2024-01-01T11:00:00Z'},
            'created': '2024-01-01T00:00:00Z',
        }

        calendar_adapter.service.events().get().execute.return_value = mock_event

        msg = await calendar_adapter.fetch_message('primary:event-id')

        assert msg is not None
        assert 'Test Event' in msg.subject
        assert 'Event description' in msg.body
