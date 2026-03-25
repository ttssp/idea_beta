
# 核心数据模型设计

## DelegationProfile（委托档位）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | VARCHAR(50) | 档位名称 |
| display_name | VARCHAR(100) | 展示名称 |
| description | TEXT | 描述 |
| profile_level | VARCHAR(20) | 档位级别（OBSERVE_ONLY/DRAFT_FIRST/APPROVE_TO_SEND/BOUNDED_AUTO/HUMAN_ONLY） |
| allowed_actions | JSONB | 允许的动作 |
| budget_config | JSONB | 预算配置 |
| escalation_rules | JSONB | 升级规则 |
| is_system_defined | BOOLEAN | 是否系统定义 |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |

## PolicyRule（策略规则）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | VARCHAR(100) | 规则名称 |
| description | TEXT | 描述 |
| scope | VARCHAR(50) | 作用域（GLOBAL/PROFILE/RELATIONSHIP/THREAD） |
| scope_id | UUID | 作用域ID |
| action | VARCHAR(100) | 动作 |
| effect | VARCHAR(20) | 效果（ALLOW/DENY/REQUIRE_APPROVAL/ESCALATE） |
| conditions | JSONB | 条件 |
| priority | INTEGER | 优先级（数字越大越高） |
| is_active | BOOLEAN | 是否激活 |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |
| created_by | UUID | 创建者 |

## ApprovalRequest（审批请求）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| thread_id | UUID | 线程ID |
| action_run_id | UUID | 动作运行ID |
| request_type | VARCHAR(50) | 请求类型（MESSAGE_SEND/ACTION_EXECUTE/BUDGET_INCREASE） |
| reason_code | VARCHAR(100) | 原因代码 |
| reason_description | TEXT | 原因描述 |
| requester_principal_id | UUID | 请求者 |
| approver_principal_id | UUID | 审批者 |
| status | VARCHAR(20) | 状态（PENDING/APPROVED/REJECTED/MODIFIED/TAKEN_OVER/CANCELLED/TIMEOUT） |
| preview | JSONB | 预览内容 |
| resolution | JSONB | 决议内容 |
| resolved_at | TIMESTAMPTZ | 决议时间 |
| resolved_by | UUID | 决议者 |
| timeout_at | TIMESTAMPTZ | 超时时间 |
| timeout_action | VARCHAR(20) | 超时动作（ESCALATE/DENY/AUTO_APPROVE） |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |

## RiskAssessment（风险评估记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| thread_id | UUID | 线程ID |
| action_run_id | UUID | 动作运行ID |
| relationship_risk | INTEGER | 关系风险（1-5） |
| action_risk | INTEGER | 动作风险（1-5） |
| content_risk | INTEGER | 内容风险（1-5） |
| consequence_risk | INTEGER | 结果风险（1-5） |
| overall_risk_level | VARCHAR(20) | 整体风险等级（LOW/MEDIUM/HIGH/CRITICAL） |
| risk_factors | JSONB | 风险因子 |
| decision_recommendation | VARCHAR(20) | 决策建议 |
| created_at | TIMESTAMPTZ | 创建时间 |

## KillSwitch（熔断开关）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| level | VARCHAR(20) | 级别（GLOBAL/PROFILE/THREAD） |
| level_id | UUID | 级别ID |
| reason | TEXT | 原因 |
| activated_by | UUID | 激活者 |
| is_active | BOOLEAN | 是否激活 |
| activated_at | TIMESTAMPTZ | 激活时间 |
| deactivated_at | TIMESTAMPTZ | 解除时间 |
| deactivated_by | UUID | 解除者 |

## DecisionTrace（决策追踪）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| thread_id | UUID | 线程ID |
| action_run_id | UUID | 动作运行ID |
| decision | VARCHAR(20) | 决策（allow/draft_only/require_approval/bounded_execution/escalate_to_human/deny） |
| decision_reason | TEXT | 决策原因 |
| steps | JSONB | 8步决策链每一步记录 |
| policy_hits | JSONB | 命中的策略 |
| risk_assessment_id | UUID | 风险评估ID（外键） |
| kill_switch_affected | BOOLEAN | 是否受熔断影响 |
| created_at | TIMESTAMPTZ | 创建时间 |
