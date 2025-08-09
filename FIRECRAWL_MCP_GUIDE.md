# Firecrawl MCP 服务使用指南

## 🔥 什么是 Firecrawl MCP？

Firecrawl MCP（Model Context Protocol）是一个专业的网站抓取服务，专门设计用于：

- **智能内容提取**：自动识别和提取主要内容
- **JavaScript 渲染**：支持动态加载的现代网站
- **结构化数据**：返回 Markdown、HTML 和 JSON 格式
- **批量处理**：高效处理多个页面
- **API 集成**：RESTful API，易于集成

## 🚀 快速开始

### 1. 获取 API 密钥

1. 访问 [Firecrawl.dev](https://firecrawl.dev)
2. 注册免费账户
3. 获取 API 密钥
4. 免费计划包含：
   - 每月 500 次抓取
   - 基础功能完整支持

### 2. 安装依赖

```bash
# 安装 Python 依赖
pip3 install -r requirements.txt

# 确保 Node.js 已安装 (用于 MCP 服务器)
node --version  # 应该显示 v16+ 版本
```

### 3. 运行 Firecrawl MCP 抓取器

```bash
# 方法1: 使用启动脚本
./run_scraper.sh
# 选择选项 1 (Firecrawl MCP 抓取器)

# 方法2: 直接运行
python3 firecrawl_scraper.py
```

## ⚙️ 配置选项

### firecrawl_config.json 配置文件

```json
{
  "scraping_config": {
    "target_url": "https://68tt.co/cn/",
    "crawl_options": {
      "includes": ["https://68tt.co/**"],
      "excludes": ["**/admin/**", "**/*.pdf"],
      "generateImgAltText": true,
      "maxDepth": 2,
      "limit": 10
    },
    "scrape_options": {
      "formats": ["markdown", "html", "rawHtml"],
      "onlyMainContent": true,
      "removeBase64Images": false
    }
  }
}
```

### 主要配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `maxDepth` | 最大抓取深度 | 2 |
| `limit` | 最大页面数量 | 10 |
| `onlyMainContent` | 只提取主要内容 | true |
| `generateImgAltText` | 生成图片描述 | true |
| `includes` | 包含的URL模式 | `["https://68tt.co/**"]` |
| `excludes` | 排除的URL模式 | `["**/admin/**"]` |

## 📊 输出格式

Firecrawl MCP 会生成以下文件：

```
firecrawl_output/
├── index.html              # 主页 HTML
├── index.md                # 主页 Markdown
├── about.html              # 关于页面 HTML
├── about.md                # 关于页面 Markdown
├── privacy.html            # 隐私页面 HTML
├── privacy.md              # 隐私页面 Markdown
├── firecrawl_raw_results.json  # 原始 API 响应
└── firecrawl_report.json   # 抓取报告
```

### 数据格式示例

```json
{
  "scraping_info": {
    "tool": "Firecrawl MCP",
    "target_url": "https://68tt.co/cn/",
    "timestamp": "2024-01-15 10:30:00",
    "total_pages": 3,
    "api_key_used": true
  },
  "pages": [
    {
      "url": "https://68tt.co/cn/",
      "title": "68 - 安全的私密聊天APP",
      "metadata": {
        "description": "安全加密的即时通讯工具",
        "language": "zh-CN"
      },
      "content_length": 1234,
      "html_length": 5678
    }
  ]
}
```

## 🔧 高级功能

### 1. 自定义抓取规则

```python
# 修改 firecrawl_scraper.py 中的配置
crawl_data = {
    "url": target_url,
    "crawlerOptions": {
        "includes": ["https://68tt.co/**"],
        "excludes": ["**/admin/**", "**/wp-admin/**"],
        "generateImgAltText": True,
        "maxDepth": 3,  # 增加抓取深度
        "limit": 20     # 增加页面限制
    },
    "pageOptions": {
        "onlyMainContent": True,
        "includeHtml": True,
        "screenshot": True  # 启用截图功能
    }
}
```

### 2. 批量抓取多个网站

```python
websites = [
    "https://68tt.co/cn/",
    "https://68tt.co/en/",
    "https://68tt.co/zh/"
]

for site in websites:
    client = FirecrawlMCPClient()
    client.config['scraping_config']['target_url'] = site
    client.run()
```

### 3. 内容过滤和处理

```python
def process_content(content):
    # 自定义内容处理逻辑
    cleaned = content.replace("广告", "")
    return cleaned

# 在 process_crawl_results 方法中使用
processed_content = process_content(page_data["markdown"])
```

## 🚨 故障排除

### 常见问题

1. **API 密钥错误**
   ```
   ❌ API请求失败: 401
   ```
   - 检查 API 密钥是否正确
   - 确认账户额度是否充足

2. **网络连接问题**
   ```
   ❌ 网络请求错误: Connection timeout
   ```
   - 检查网络连接
   - 使用代理或 VPN

3. **Node.js 未安装**
   ```
   ❌ Node.js/NPM 未安装
   ```
   - 安装 Node.js: https://nodejs.org
   - 确保版本 >= 16

4. **抓取限制**
   ```
   ❌ 爬取任务失败: Rate limit exceeded
   ```
   - 降低抓取频率
   - 升级到付费计划

### 调试模式

```bash
# 启用详细日志
export FIRECRAWL_DEBUG=1
python3 firecrawl_scraper.py
```

## 💡 最佳实践

### 1. 合理设置限制
- **小网站**: maxDepth=2, limit=10
- **中等网站**: maxDepth=3, limit=50
- **大型网站**: maxDepth=2, limit=100

### 2. 优化性能
- 使用 `onlyMainContent=true` 减少噪音
- 设置合适的 `excludes` 规则
- 避免抓取不必要的文件类型

### 3. 内容质量
- 启用 `generateImgAltText` 提高可访问性
- 使用多种输出格式 (HTML + Markdown)
- 定期更新抓取内容

### 4. 成本控制
- 监控 API 使用量
- 设置合理的 limit 参数
- 使用缓存避免重复抓取

## 📈 与其他工具对比

| 特性 | Firecrawl MCP | 基础抓取器 | 自定义 MCP |
|------|---------------|------------|------------|
| JavaScript 支持 | ✅ 完整 | ❌ 无 | ❌ 无 |
| 内容提取质量 | ✅ 智能 | ⚠️ 基础 | ⚠️ 基础 |
| 批量处理 | ✅ 高效 | ⚠️ 中等 | ✅ 高效 |
| 配置复杂度 | ⚠️ 中等 | ✅ 简单 | ⚠️ 中等 |
| 成本 | 💰 付费 | ✅ 免费 | ✅ 免费 |
| 维护需求 | ✅ 低 | ⚠️ 中等 | ⚠️ 高 |

## 🔗 相关链接

- [Firecrawl 官网](https://firecrawl.dev)
- [Firecrawl API 文档](https://docs.firecrawl.dev)
- [MCP 协议规范](https://modelcontextprotocol.io)
- [68tt.co 目标网站](https://68tt.co/cn/)

## 📞 支持

如果遇到问题：

1. 查看本地生成的日志文件
2. 检查 `firecrawl_report.json` 报告
3. 参考官方文档
4. 联系 Firecrawl 支持团队

---

**注意**: 使用 Firecrawl MCP 服务时请遵守目标网站的使用条款和相关法律法规。
