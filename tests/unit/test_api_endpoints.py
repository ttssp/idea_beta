"""API 端点回归测试"""

from uuid import uuid4

from myproj.api.v1.events import _thread_service


def test_root_and_health_endpoints(client):
    root = client.get("/")
    health = client.get("/health")

    assert root.status_code == 200
    assert root.json()["docs"] == "/docs"

    assert health.status_code == 200
    assert health.json()["status"] == "healthy"


def test_events_endpoint_applies_offset_and_limit(client):
    thread, _ = _thread_service.create_thread(
        title="测试事件分页",
        owner_id=uuid4(),
    )
    _thread_service.update_summary(thread.id, "summary-1")
    _thread_service.update_risk_level(thread.id, risk_level=thread.risk_level, reason="keep-low")
    _thread_service.add_participant(thread.id, uuid4())

    response = client.get(
        f"/api/v1/threads/{thread.id.value}/events",
        params={"offset": 1, "limit": 2},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 4
    assert len(payload["items"]) == 2
    assert payload["items"][0]["sequence_number"] == 2
    assert payload["items"][1]["sequence_number"] == 3


def test_events_summary_reflects_created_events(client):
    thread, _ = _thread_service.create_thread(
        title="测试事件摘要",
        owner_id=uuid4(),
    )
    _thread_service.update_summary(thread.id, "summary")

    response = client.get(f"/api/v1/threads/{thread.id.value}/events/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_events"] == 2
    assert payload["first_event_at"] is not None
    assert payload["last_event_at"] is not None


def test_send_message_twice_returns_validation_error(client):
    thread_id = uuid4()
    sender_id = uuid4()

    created = client.post(
        f"/api/v1/threads/{thread_id}/messages",
        json={
            "sender_principal_id": str(sender_id),
            "content": "hello",
            "subject": "test",
            "channel": "internal",
            "authored_mode": "human_authored_human_sent",
        },
    )
    assert created.status_code == 201

    message_id = created.json()["id"]

    first_send = client.post(f"/api/v1/threads/{thread_id}/messages/{message_id}/send")
    second_send = client.post(f"/api/v1/threads/{thread_id}/messages/{message_id}/send")

    assert first_send.status_code == 200
    assert second_send.status_code == 422
    assert second_send.json()["error"] == "validation_error"


def test_update_sent_message_returns_validation_error(client):
    thread_id = uuid4()
    sender_id = uuid4()

    created = client.post(
        f"/api/v1/threads/{thread_id}/messages",
        json={
            "sender_principal_id": str(sender_id),
            "content": "hello",
            "subject": "draft",
            "channel": "internal",
            "authored_mode": "human_authored_human_sent",
        },
    )
    assert created.status_code == 201

    message_id = created.json()["id"]
    client.post(f"/api/v1/threads/{thread_id}/messages/{message_id}/send")

    updated = client.patch(
        f"/api/v1/threads/{thread_id}/messages/{message_id}",
        json={"content": "new content"},
    )

    assert updated.status_code == 422
    assert updated.json()["message"] == "Cannot update non-draft message"


def test_update_principal_can_toggle_active_state(client):
    created = client.post(
        "/api/v1/principals",
        json={
            "principal_type": "human",
            "display_name": "Alice",
            "email": "alice@example.com",
        },
    )
    assert created.status_code == 201

    principal_id = created.json()["id"]
    updated = client.patch(
        f"/api/v1/principals/{principal_id}",
        json={
            "is_active": False,
            "timezone": "Asia/Shanghai",
            "locale": "zh-CN",
        },
    )

    assert updated.status_code == 200
    payload = updated.json()
    assert payload["is_active"] is False
    assert payload["timezone"] == "Asia/Shanghai"
    assert payload["locale"] == "zh-CN"
    assert payload["version"] == 4
