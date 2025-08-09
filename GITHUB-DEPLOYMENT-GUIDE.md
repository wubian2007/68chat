# GitHub 部署指南

## ❌ GitHub Pages 限制说明

**重要**: GitHub Pages **不支持 Node.js 后台管理系统**，因为：

1. **静态托管限制**: 只支持 HTML、CSS、JS 静态文件
2. **无服务器环境**: 不能运行 Node.js、Express 等后端代码
3. **无文件写入**: 不支持配置保存、文件上传等操作
4. **无数据库**: 不支持用户认证和会话管理

## 🔄 推荐部署方案

### 方案1: 分离部署（推荐）

#### 前端部署 - GitHub Pages
```bash
# 1. 创建 gh-pages 分支
git checkout -b gh-pages

# 2. 只保留前端文件
git rm -r node_modules routes views server.js package.json
git rm -r logs config-demo.env start-admin.sh

# 3. 创建 GitHub Pages 配置
echo "68chat.github.io" > CNAME  # 如果有自定义域名

# 4. 提交并推送
git add .
git commit -m "🚀 部署前端到 GitHub Pages"
git push origin gh-pages
```

#### 后台部署 - 云服务
选择以下任一平台部署后台管理系统：

**推荐平台**:
- **Vercel** (免费，推荐)
- **Railway** (免费额度)
- **Render** (免费额度)
- **Heroku** (付费)
- **阿里云/腾讯云** (按需付费)

### 方案2: 静态配置管理

创建基于 GitHub Actions 的配置管理系统：

#### 创建 GitHub Actions 工作流

<function_calls>
<invoke name="run_terminal_cmd">
<parameter name="command">mkdir -p .github/workflows
