
"""
Policy &amp; Control Module - Main Entry Point

Example usage and testing
"""
from uuid import uuid4
from .controller import PolicyControlController
from .common.constants import Decision, DelegationLevel


def main():
    """示例：展示Policy &amp; Control模块的使用"""
    print("=" * 60)
    print("Policy &amp; Control Module")
    print("=" * 60)

    # 创建控制器
    controller = PolicyControlController()
    print("\n✓ Controller initialized")

    # 查看可用的委托档位
    print("\n--- Delegation Profiles ---")
    profiles = controller.delegation_service.list_profiles()
    for profile in profiles:
        print(f"  - {profile.name}: {profile.display_name} ({profile.profile_level.value})")

    # 创建测试线程ID
    thread_id = uuid4()
    print(f"\n--- Test Thread: {thread_id} ---")

    # 设置线程的委托档位
    profile = controller.delegation_service.get_profile_by_name("approve_to_send")
    if profile:
        controller.delegation_service.bind_thread_profile(thread_id, profile.id)
        print(f"✓ Bound to profile: {profile.name}")

    # 测试1: 低风险动作
    print("\n--- Test 1: Low risk action ---")
    result = controller.evaluate_action(
        thread_id=thread_id,
        action="send_message",
        action_type="send_message",
        content="Hi, just checking in to confirm our meeting tomorrow.",
        relationship_class="colleague",
    )
    print(f"  Decision: {result['decision'].value}")
    print(f"  Reason: {result['decision_reason']}")
    print(f"  Trace ID: {result['decision_trace_id']}")

    # 测试2: 高风险内容
    print("\n--- Test 2: High risk content ---")
    result = controller.evaluate_action(
        thread_id=thread_id,
        action="send_message",
        action_type="send_message",
        content="I agree to pay $10,000 for this service.",
        relationship_class="client",
    )
    print(f"  Decision: {result['decision'].value}")
    print(f"  Reason: {result['decision_reason']}")

    # 测试3: 激活熔断
    print("\n--- Test 3: Kill Switch ---")
    user_id = uuid4()
    from .common.constants import KillSwitchLevel
    controller.kill_switch_service.activate(
        level=KillSwitchLevel.THREAD,
        level_id=thread_id,
        reason="Emergency stop",
        activated_by=user_id,
    )
    print("✓ Kill switch activated")

    result = controller.evaluate_action(
        thread_id=thread_id,
        action="send_message",
        action_type="send_message",
        content="Test message",
    )
    print(f"  Decision: {result['decision'].value}")
    print(f"  Reason: {result['decision_reason']}")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
