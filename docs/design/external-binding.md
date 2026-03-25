
# External Binding 设计

&gt; 文档用途：定义外部消息到内部Thread的映射规则、去重策略和解析机制

## 1. 核心问题

### 1.1 为什么需要External Binding？

如果没有统一的`ExternalBinding`模型，系统会遇到以下问题：
- 同一封邮件被识别成多个Thread
- 一个外部回复找不到正确的Thread
- 重发动作与历史动作混淆

### 1.2 核心原则

- **内部Thread ID永远独立存在**：不依赖外部系统的ID
- **外部Key仅作为绑定对象**：用于查找和关联
- **所有外部事件先进入Ingress**：再由Resolver映射到内部Thread

---

## 2. External Thread Key 生成策略

### 2.1 Email 渠道

| 字段 | 说明 | 优先级 |
|------|------|--------|
| `Thread-ID` | Gmail/Email标准Thread ID | 1 |
| `References` header | 邮件引用链 | 2 |
| `In-Reply-To` header | 直接回复的消息ID | 3 |
| `Message-ID` + Subject | 主题匹配（降级方案） | 4 |

**算法：**
```python
def get_email_thread_key(message: EmailMessage) -&gt; str:
    # 1. 优先使用已有的Thread-ID
    if message.thread_id:
        return f"email:{message.thread_id}"

    # 2. 从References中提取
    if message.references:
        # References是空格分隔的Message-ID列表
        refs = message.references.split()
        if refs:
            # 使用最旧的Message-ID作为线程根
            return f"email:{refs[0]}"

    # 3. 使用In-Reply-To
    if message.in_reply_to:
        return f"email:{message.in_reply_to}"

    # 4. 降级：使用当前Message-ID + Subject哈希
    subject_hash = hashlib.md5(message.subject.encode()).hexdigest()[:12]
    return f"email:{message.message_id}:{subject_hash}"
```

### 2.2 Calendar 渠道

| 字段 | 说明 |
|------|------|
| `iCalUID` | 全局唯一日历事件ID |
| `Event ID` + Calendar ID | Google Calendar的事件+日历ID |

**算法：**
```python
def get_calendar_thread_key(event: CalendarEvent) -&gt; str:
    if event.ical_uid:
        return f"calendar:{event.ical_uid}"
    return f"calendar:{event.calendar_id}:{event.event_id}"
```

---

## 3. 去重策略

### 3.1 InboxEvent去重

**三层去重机制：**

1. **数据库UNIQUE约束**
   ```sql
   UNIQUE(external_message_key)
   ```

2. **幂等键缓存**
   ```python
   # Redis缓存24小时
   idempotency_key = hash(channel_type + external_message_key)
   ```

3. **Webhook签名验证**
   - Gmail: Pub/Sub消息验证
   - Outlook: Validation-Token验证

### 3.2 ExternalBinding去重

**约束：**
```sql
UNIQUE(channel_type, external_thread_key)
```

**创建逻辑：**
```python
async def bind_thread(
    thread_id: UUID,
    channel_type: str,
    external_thread_key: str,
    external_message_key: str = None,
    binding_type: str = "primary"
) -&gt; ExternalBinding:
    # 1. 检查是否已存在
    existing = await db.execute(
        select(ExternalBinding).where(
            ExternalBinding.channel_type == channel_type,
            ExternalBinding.external_thread_key == external_thread_key
        )
    )
    if existing.scalar_one_or_none():
        # 已绑定，返回现有绑定
        return existing

    # 2. 创建新绑定
    binding = ExternalBinding(
        thread_id=thread_id,
        channel_type=channel_type,
        external_thread_key=external_thread_key,
        external_message_key=external_message_key,
        binding_type=binding_type
    )
    db.add(binding)
    await db.commit()
    return binding
```

---

## 4. External Resolver 解析流程

### 4.1 完整解析流程

```
┌─────────────────────────────────────────────────────────┐
│                    Ingress Webhook                        │
│              (接收外部事件，去重，写入Inbox)              │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              1. 提取 external_message_key                 │
│              2. 提取 external_thread_key                  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ├─┐
                      │ │ 已有external_thread_key?
                      │ ├─是──────────────────────────┐
                      │ │                              │
                      │ ▼                              ▼
                      │ ┌─────────────────────┐  ┌─────────────────────┐
                      │ │  2. 查找External   │  │  3. 通过Message-ID  │
                      │ │     Binding         │  │     查找关联Thread  │
                      │ └──────────┬──────────┘  └──────────┬──────────┘
                      │            │                         │
                      │            └──────────┬──────────────┘
                      │                       │
                      │                       ▼
                      │              找到Thread了吗?
                      │                       │
                      ├─┐                     ├─┐
                      │ │ 否                  │ │ 是
                      │ ▼                     │ ▼
                      │ ┌──────────────────┐ │ ┌──────────────────┐
                      │ │ 4. 创建新Thread? │ │ 5. 更新Thread     │
                      │ │    (策略决定)    │ │    状态/摘要      │
                      │ └──────────────────┘ │ └──────────────────┘
                      │                       │
                      └──────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ 6. 标记InboxEvent为     │
                    │    processed             │
                    └─────────────────────────┘
```

### 4.2 解析策略接口

```python
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from uuid import UUID

class ResolutionStrategy(ABC):
    @abstractmethod
    def extract_external_keys(
        self,
        payload: dict
    ) -&gt; Tuple[Optional[str], Optional[str]]:
        """
        从payload中提取external_thread_key和external_message_key
        返回: (external_thread_key, external_message_key)
        """
        pass

    @abstractmethod
    async def find_related_thread(
        self,
        payload: dict,
        db: AsyncSession
    ) -&gt; Optional[UUID]:
        """
        通过其他线索（如In-Reply-To）查找关联Thread
        """
        pass
```

### 4.3 Email解析策略实现

```python
class EmailResolutionStrategy(ResolutionStrategy):
    def extract_external_keys(self, payload: dict) -&gt; Tuple[Optional[str], Optional[str]]:
        headers = payload.get("payload", {}).get("headers", [])

        message_id = self._get_header(headers, "Message-ID")
        thread_id = self._get_header(headers, "Thread-ID")
        references = self._get_header(headers, "References")
        in_reply_to = self._get_header(headers, "In-Reply-To")

        external_message_key = f"email:{message_id}" if message_id else None

        # 计算external_thread_key
        external_thread_key = None
        if thread_id:
            external_thread_key = f"email:{thread_id}"
        elif references:
            # 使用References中的第一个Message-ID
            first_ref = references.split()[0] if references.split() else None
            if first_ref:
                external_thread_key = f"email:{first_ref}"
        elif in_reply_to:
            external_thread_key = f"email:{in_reply_to}"
        elif message_id:
            # 新线程，使用当前Message-ID
            external_thread_key = f"email:{message_id}"

        return external_thread_key, external_message_key

    async def find_related_thread(
        self,
        payload: dict,
        db: AsyncSession
    ) -&gt; Optional[UUID]:
        headers = payload.get("payload", {}).get("headers", [])
        in_reply_to = self._get_header(headers, "In-Reply-To")

        if in_reply_to:
            # 通过In-Reply-To查找之前的绑定
            msg_key = f"email:{in_reply_to}"
            result = await db.execute(
                select(ExternalBinding.thread_id)
                .where(ExternalBinding.external_message_key == msg_key)
            )
            thread_id = result.scalar_one_or_none()
            if thread_id:
                return thread_id

        return None

    def _get_header(self, headers: list, name: str) -&gt; Optional[str]:
        for h in headers:
            if h.get("name", "").lower() == name.lower():
                return h.get("value")
        return None
```

---

## 5. 测试用例

### 5.1 Email解析测试（EB-001 至 EB-005）

**EB-001: 有Thread-ID的邮件**
```
Input: 邮件包含Thread-ID header
Expected: 使用Thread-ID作为external_thread_key
```

**EB-002: 有References的回复邮件**
```
Input: 邮件包含References header
Expected: 使用References第一个ID作为external_thread_key
```

**EB-003: 有In-Reply-To的邮件**
```
Input: 邮件包含In-Reply-To header
Expected: 使用In-Reply-To作为external_thread_key
```

**EB-004: 新线程邮件**
```
Input: 无Thread-ID/References/In-Reply-To
Expected: 使用Message-ID作为external_thread_key
```

**EB-005: 找到已有绑定**
```
Input: external_thread_key已绑定到Thread 123
Expected: 解析到Thread 123，不创建新Thread
```

---

## 6. 绑定类型

| binding_type | 说明 | 使用场景 |
|--------------|------|----------|
| `primary` | 主绑定 | 线程创建时的初始绑定 |
| `reply` | 回复绑定 | 后续回复追加到同一线程 |
| `related` | 关联绑定 | 相关但不同的线程 |

---

## 7. 同步状态

| sync_state | 说明 |
|------------|------|
| `active` | 活跃同步 |
| `paused` | 暂停同步 |
| `archived` | 归档 |

