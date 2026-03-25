
# Email/Calendar API 能力分析

&gt; 文档用途：汇总和分析Email/Calendar API的能力、限制、认证方式和推送机制

## 1. Gmail API

### 1.1 能力概览

| 功能 | 支持 | 说明 |
|------|------|------|
| 发送邮件 | ✓ | 支持MIME格式、threading |
| 接收邮件 | ✓ | 通过History API增量同步 |
| 搜索邮件 | ✓ | 支持Gmail搜索语法 |
| 标签管理 | ✓ | 创建/修改/删除标签 |
| 草稿管理 | ✓ | 保存和修改草稿 |

### 1.2 配额限制

| 限制项 | 配额 | 说明 |
|--------|------|------|
| 每日配额 | 2,000,000 units/day | 发送 = 100 units，读取 = 5 units |
| 发送速率 | ~2000 emails/day | 超出会返回429 |
| 并发请求 | 未明确限制 | 建议使用指数退避 |

### 1.3 认证方式

- **OAuth 2.0**：推荐方式
  - Scopes:
    - `gmail.send` - 仅发送
    - `gmail.readonly` - 仅读取
    - `gmail.modify` - 修改（不含删除）
    - `gmail.compose` - 写草稿
    - `gmail.full` - 完全访问

### 1.4 推送机制

- **Cloud Pub/Sub**：实时推送
  - 配置watch请求订阅邮箱变化
  - 支持`historyId`增量拉取
  - 延迟通常&lt; 10秒

### 1.5 幂等支持

| 功能 | 幂等方式 |
|------|----------|
| 发送邮件 | 指定`threadId`避免重复线程 |
| 消息ID | `Message-ID` header用于去重 |
| History | `historyId`用于增量同步 |

---

## 2. Outlook Mail API

### 2.1 能力概览

| 功能 | 支持 | 说明 |
|------|------|------|
| 发送邮件 | ✓ | 支持Microsoft Graph |
| 接收邮件 | ✓ | Webhook推送 |
| 文件夹管理 | ✓ | 自定义文件夹 |
| 规则管理 | ✓ | 服务端规则 |

### 2.2 配额限制

| 限制项 | 配额 |
|--------|------|
| 请求速率 | 10,000 requests/10 min |
| 并发请求 | 可申请提升 |
| 邮件大小 | 150 MB max |

### 2.3 认证方式

- **OAuth 2.0 (Microsoft Identity Platform)**
  - Scopes:
    - `Mail.Send` - 发送邮件
    - `Mail.ReadWrite` - 读写邮件
    - `Mail.ReadBasic` - 只读基础信息

### 2.4 推送机制

- **Webhooks**：实时推送
  - 订阅特定资源变化
  - 验证token机制防止滥用
  - 支持订阅续期

---

## 3. Google Calendar API

### 3.1 能力概览

| 功能 | 支持 | 说明 |
|------|------|------|
| 创建事件 | ✓ | 支持iCalUID、会议链接 |
| 更新事件 | ✓ | Patch/Update两种方式 |
| 删除事件 | ✓ | 支持单次/全部实例 |
| 查询忙闲 | ✓ | FreeBusy查询 |
| 日历列表 | ✓ | 管理多个日历 |
| 事件提醒 | ✓ | Email/Popup提醒 |
| 会议集成 | ✓ | Google Meet自动创建 |

### 3.2 配额限制

| 限制项 | 配额 |
|--------|------|
| 每日配额 | 1,000,000 requests/day |
| 每分钟配额 | 30,000 requests/minute |
| 每用户每秒 | 可配置 |

### 3.3 认证方式

- **OAuth 2.0**
  - Scopes:
    - `calendar.events` - 事件读写
    - `calendar.readonly` - 只读
    - `calendar` - 完整访问

### 3.4 推送机制

- **Push Notifications**：实时推送
  - 使用watch方法订阅
  - 支持`syncToken`增量同步
  - 地址需要HTTPS

### 3.5 幂等支持

| 功能 | 幂等方式 |
|------|----------|
| 创建事件 | `iCalUID` - 全局唯一标识符 |
| 更新事件 | `sequence` - 乐观锁版本号 |
| 同步 | `syncToken` - 增量同步 |

---

## 4. Outlook Calendar API

### 4.1 能力概览

| 功能 | 支持 |
|------|------|
| 创建事件 | ✓ |
| 更新事件 | ✓ |
| 取消事件 | ✓ |
| 忙闲查询 | ✓ |
| 日历权限 | ✓ |
| Teams会议 | ✓ |

### 4.2 认证方式

- **OAuth 2.0 (Microsoft Identity Platform)**
  - Scopes:
    - `Calendars.ReadWrite` - 日历读写
    - `Calendars.Read` - 只读

---

## 5. 首发决策

### 5.1 首发渠道选择

| 渠道 | 优先级 | 原因 |
|------|--------|------|
| **Gmail** | P0 | 事务型邮件占比高，API成熟 |
| **Google Calendar** | P0 | 时间协调核心场景 |
| **Outlook Mail** | P1 | 企业用户需求 |
| **Outlook Calendar** | P1 | 企业用户需求 |

### 5.2 分阶段上线策略

1. **Phase 1**: Gmail + Google Calendar 最小闭环
2. **Phase 2**: Outlook Mail + Outlook Calendar
3. **Phase 3**: Task/Doc 集成（二选一）

---

## 6. API集成关键点

### 6.1 幂等控制

| 渠道 | 幂等键 |
|------|--------|
| Gmail | Message-ID + Thread-ID |
| Google Calendar | iCalUID + sequence |
| Outlook | Client-Trace-ID |

### 6.2 异常处理

- **429 Too Many Requests**: 指数退避（2^n秒）
- **401 Unauthorized**: 自动刷新token
- **403 Forbidden**: 检查scope，记录审计日志
- **404 Not Found**: 资源已删除，清理绑定

### 6.3 Webhook签名验证

| 渠道 | 验证方式 |
|------|----------|
| Gmail | Pub/Sub push (GCP IAM) |
| Google Calendar | X-Goog-Channel-ID + token |
| Outlook | Validation-Token + HMAC |

