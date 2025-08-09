#!/bin/bash

# 68tt.co 网站内容抓取启动脚本

echo "🔧 68tt.co 网站内容抓取工具"
echo "=================================="

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    echo "请安装 Python 3.7 或更高版本"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"

# 检查并安装依赖
echo "📦 检查依赖包..."
if ! python3 -c "import requests, bs4, aiohttp" 2>/dev/null; then
    echo "📥 安装依赖包..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
else
    echo "✅ 依赖包已安装"
fi

echo ""
echo "选择抓取模式:"
echo "1) Firecrawl MCP 抓取器 (推荐) - 专业级网站抓取"
echo "2) 基础抓取器 - 完整网站克隆"
echo "3) 自定义 MCP 抓取器 - 结构化内容提取"
echo "4) 运行所有模式"
echo ""

read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo "🔥 启动 Firecrawl MCP 抓取器..."
        python3 firecrawl_scraper.py
        ;;
    2)
        echo "🚀 启动基础抓取器..."
        python3 site_scraper.py
        ;;
    3)
        echo "🚀 启动自定义 MCP 抓取器..."
        python3 mcp_scraper.py
        ;;
    4)
        echo "🔥 启动 Firecrawl MCP 抓取器..."
        python3 firecrawl_scraper.py
        echo ""
        echo "🚀 启动基础抓取器..."
        python3 site_scraper.py
        echo ""
        echo "🚀 启动自定义 MCP 抓取器..."
        python3 mcp_scraper.py
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "✅ 抓取完成!"
echo "📁 检查输出目录:"
echo "   - firecrawl_output/ (Firecrawl MCP 结果)"
echo "   - scraped_68tt/ (基础抓取结果)"
echo "   - mcp_scraped/ (自定义 MCP 抓取结果)"
