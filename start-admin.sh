#!/bin/bash

# 68Chat 后台管理系统启动脚本

echo "🚀 启动 68Chat 后台管理系统..."

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误: Node.js 未安装"
    echo "请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

# 检查 npm 是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: npm 未安装"
    exit 1
fi

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo "正在从模板创建 .env 文件..."
    
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ 已创建 .env 文件，请编辑其中的配置"
        echo "📝 重要: 请修改以下配置项："
        echo "   - ADMIN_USERNAME (管理员用户名)"
        echo "   - ADMIN_PASSWORD (管理员密码)"
        echo "   - JWT_SECRET (JWT密钥)"
        echo "   - ADMIN_PATH (后台路径)"
        echo "   - COOKIE_SECRET (Cookie密钥)"
        echo ""
        echo "按任意键继续..."
        read -n 1 -s
    else
        echo "❌ 错误: env.example 文件不存在"
        exit 1
    fi
fi

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖包..."
    npm install
    
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p logs
mkdir -p public

# 检查 data.json 是否存在
if [ ! -f "data.json" ]; then
    echo "⚠️  警告: data.json 配置文件不存在"
    echo "系统将使用默认配置启动"
fi

# 显示配置信息
echo ""
echo "📋 系统配置信息:"
echo "   端口: $(grep PORT .env | cut -d '=' -f2 || echo '3001')"
echo "   后台路径: $(grep ADMIN_PATH .env | cut -d '=' -f2 || echo '/admin-93874-control')"
echo "   管理员: $(grep ADMIN_USERNAME .env | cut -d '=' -f2 || echo 'admin')"
echo ""

# 启动服务器
echo "🎯 启动服务器..."
echo "按 Ctrl+C 停止服务"
echo ""

# 检查是否安装了 nodemon
if command -v nodemon &> /dev/null && [ "$NODE_ENV" != "production" ]; then
    echo "🔄 开发模式启动 (使用 nodemon)..."
    nodemon server.js
else
    echo "🚀 生产模式启动..."
    node server.js
fi
