#!/bin/bash
# E5 健康检查脚本

E5_HOST=${E5_HOST:-localhost}
E5_PORT=${E5_PORT:-8085}

echo "检查 E5 服务健康状态..."
echo "地址: http://${E5_HOST}:${E5_PORT}"
echo ""

# 检查健康接口
if command -v curl &> /dev/null; then
    HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://${E5_HOST}:${E5_PORT}/health")

    if [ "$HEALTH_RESPONSE" = "200" ]; then
        echo "✅ 健康检查通过"
        echo ""
        echo "服务详情："
        curl -s "http://${E5_HOST}:${E5_PORT}/health"
        echo ""
        echo "就绪检查："
        curl -s "http://${E5_HOST}:${E5_PORT}/ready"
        echo ""
        exit 0
    else
        echo "❌ 健康检查失败 (HTTP $HEALTH_RESPONSE)"
        exit 1
    fi
else
    echo "⚠️  curl 未安装，无法进行健康检查"
    exit 1
fi
