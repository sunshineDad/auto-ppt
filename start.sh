#!/bin/bash

# AI-PPT System 快速启动脚本
# Quick start script for AI-PPT System

set -e

echo "🎯 AI-PPT System 快速启动"
echo "=========================="

# 检查 Python 和 Node.js
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.8+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 16+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装 npm"
    exit 1
fi

echo "✅ 环境检查通过"

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ 后端依赖文件不存在"
    exit 1
fi

# 检查 Python 依赖
echo "🔍 检查后端依赖..."
cd backend
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "📦 安装后端依赖..."
    pip3 install -r requirements.txt
fi
cd ..

echo "✅ 依赖检查完成"

# 构建前端
if [ ! -d "dist" ] || [ "$1" = "--rebuild" ]; then
    echo "🔨 构建前端..."
    npm run build
fi

# 启动模式选择
MODE=${1:-development}

case $MODE in
    "dev"|"development")
        echo "🚀 启动开发模式..."
        python3 deploy.py development
        ;;
    "prod"|"production")
        echo "🌍 启动生产模式..."
        python3 deploy.py production
        ;;
    "docker")
        echo "🐳 使用 Docker 启动..."
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker 未安装"
            exit 1
        fi
        docker-compose up -d
        echo "✅ Docker 服务已启动"
        echo "🌐 前端: http://localhost"
        echo "🔧 后端: http://localhost:8000"
        ;;
    "--help"|"-h")
        echo "用法: $0 [模式]"
        echo ""
        echo "模式:"
        echo "  dev, development  - 开发模式 (默认)"
        echo "  prod, production  - 生产模式"
        echo "  docker           - Docker 模式"
        echo "  --rebuild        - 重新构建前端"
        echo "  --help, -h       - 显示帮助"
        echo ""
        echo "示例:"
        echo "  $0                # 开发模式"
        echo "  $0 production     # 生产模式"
        echo "  $0 docker         # Docker 模式"
        echo "  $0 --rebuild      # 重新构建并启动"
        ;;
    *)
        echo "❌ 未知模式: $MODE"
        echo "使用 $0 --help 查看帮助"
        exit 1
        ;;
esac