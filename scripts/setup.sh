#!/bin/bash
# E5 项目设置脚本

set -e

echo "======================================"
echo "E5 - AI/Agent Intelligence Layer"
echo "======================================"
echo ""

# 检查Node.js版本
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2)
echo "✅ Node.js 版本: $NODE_VERSION"

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装"
    exit 1
fi

echo ""
echo "正在安装依赖..."
npm install

echo ""
echo "======================================"
echo "✅ 依赖安装完成！"
echo "======================================"
echo ""
echo "下一步："
echo "1. 复制 .env.example 为 .env"
echo "   cp .env.example .env"
echo ""
echo "2. 编辑 .env 文件，填入你的 API keys"
echo ""
echo "3. 启动开发服务器"
echo "   npm run dev"
echo ""
echo "4. 或使用 Docker 启动"
echo "   docker-compose up"
echo ""
