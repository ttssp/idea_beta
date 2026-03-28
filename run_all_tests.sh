#!/bin/bash

# Communication OS v1 - 一键测试脚本
# 版本: 1.1
# 日期: 2026-03-28

set -e

echo "=========================================="
echo "  Communication OS v1 - 测试套件"
echo "=========================================="
echo ""

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_DIR="/Users/admin/codes/idea_beta/myproj"
cd "$PROJECT_DIR"

# 设置 PYTHONPATH
export PYTHONPATH="$PROJECT_DIR/src:$PROJECT_DIR/backend/e3:$PYTHONPATH"

echo "📁 项目目录: $PROJECT_DIR"
echo "🐍 PYTHONPATH: $PYTHONPATH"
echo ""

# 统计信息
CORE_TEST_COUNT=0
E3_TEST_COUNT=0

# 运行测试函数
run_test_suite() {
    local name=$1
    local dir=$2
    local cmd=$3

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧪 运行: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [ -n "$dir" ]; then
        cd "$dir"
    fi

    set +e
    output=$(eval "$cmd" 2>&1)
    local exit_code=$?
    set -e

    if [ -n "$dir" ]; then
        cd "$PROJECT_DIR"
    fi

    # 提取测试数量
    if echo "$output" | grep -q "passed in"; then
        test_count=$(echo "$output" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+")
        if [ -z "$test_count" ]; then
            test_count=$(echo "$output" | grep -oE "[0-9]+ tests passed" | grep -oE "[0-9]+")
        fi
        if [ -n "$test_count" ]; then
            if [ -z "$dir" ]; then
                CORE_TEST_COUNT=$((CORE_TEST_COUNT + test_count))
            else
                E3_TEST_COUNT=$((E3_TEST_COUNT + test_count))
            fi
        fi
    fi

    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ $name - 通过${NC}"
        echo "$output" | tail -5
        return 0
    else
        echo -e ""
        echo -e "${RED}❌ $name - 失败${NC}"
        echo "$output"
        return 1
    fi
}

# ===== 快速模式: 只运行完整测试套件 =====
if [ "$1" = "--quick" ] || [ "$1" = "-q" ]; then
    echo -e "${BLUE}⚡ 快速模式 - 只运行完整测试套件${NC}"

    echo ""
    echo "1️⃣  完整核心测试套件 (166 tests)"
    run_test_suite "完整核心测试" "" "python -m pytest tests/ -v --tb=short"

    echo ""
    echo "2️⃣  完整 E3 测试套件 (45 tests)"
    run_test_suite "完整 E3 测试" "backend/e3" "python -m pytest tests/ -v --tb=short"

else
    # ===== 详细模式: 运行所有测试套件 =====
    echo -e "${BLUE}📋 详细模式 - 运行所有测试套件${NC}"

    # ===== 测试 1: 核心单元测试 =====
    echo ""
    echo "1️⃣  合同测试"
    run_test_suite "合同测试" "" "python -m pytest tests/unit/contracts/ -v --tb=short"

    echo ""
    echo "2️⃣  治理层测试"
    run_test_suite "治理着陆区测试" "" "python -m pytest tests/unit/governance/ -v --tb=short"

    echo ""
    echo "3️⃣  仓储层测试"
    run_test_suite "仓储测试" "" "python -m pytest tests/unit/repositories/ -v --tb=short"

    echo ""
    echo "4️⃣  其他核心测试"
    run_test_suite "核心测试" "" "python -m pytest tests/unit/test_thread.py tests/unit/test_state_machine.py tests/unit/test_event_store.py tests/unit/test_api_endpoints.py tests/unit/test_db_session.py -v --tb=short"

    echo ""
    echo "5️⃣  核心集成测试"
    run_test_suite "端到端合同流程" "" "python -m pytest tests/integration/test_contract_flow.py -v --tb=short"

    # ===== 测试 2: E3 测试 =====
    echo ""
    echo "6️⃣  E3 Action State Machine"
    run_test_suite "E3 Action State Machine" "backend/e3" "python -m pytest tests/unit/test_action_state_machine.py -v --tb=short"

    echo ""
    echo "7️⃣  E3 ActionEnvelope 测试"
    run_test_suite "E3 ActionEnvelope" "backend/e3" "python -m pytest tests/unit/test_action_envelope.py -v --tb=short"

    echo ""
    echo "8️⃣  E3 Idempotency 测试"
    run_test_suite "E3 Idempotency" "backend/e3" "python -m pytest tests/unit/test_idempotency.py -v --tb=short"

    echo ""
    echo "9️⃣  E3 集成测试"
    run_test_suite "E3 适配器集成" "backend/e3" "python -m pytest tests/integration/ -v --tb=short"

    # ===== 完整测试套件 =====
    echo ""
    echo "🔟  完整核心测试套件"
    run_test_suite "完整核心测试" "" "python -m pytest tests/ -v --tb=short"

    echo ""
    echo "1️⃣1️⃣  完整 E3 测试套件"
    run_test_suite "完整 E3 测试" "backend/e3" "python -m pytest tests/ -v --tb=short"
fi

# ===== 总结 =====
echo ""
echo "=========================================="
echo "  📊 测试总结"
echo "=========================================="
echo ""
echo -e "${BOLD}测试统计:${NC}"
echo "  - 核心测试: ${CORE_TEST_COUNT:-166} 个"
echo "  - E3 测试: ${E3_TEST_COUNT:-45} 个"
echo "  - 总计: $((CORE_TEST_COUNT + E3_TEST_COUNT)) 个"
echo ""
echo -e "${GREEN}✅ 所有测试已运行完成!${NC}"
echo ""
echo "📖 相关文档:"
echo "   - 测试文档: docs/testing/TEST_DOCUMENTATION.md"
echo "   - 测试手册: docs/testing/TEST_MANUAL.md"
echo "   - 验收报告: docs/engineering/PHASE3_ACCEPTANCE.md"
echo ""
echo "🎯 快速命令:"
echo "   - 快速模式: ./run_all_tests.sh --quick"
echo "   - 只运行核心测试: python -m pytest tests/ -v"
echo "   - 只运行 E3 测试: cd backend/e3 && python -m pytest tests/ -v"
echo "   - 运行特定测试: python -m pytest tests/integration/test_contract_flow.py -v"
echo ""

