# 68Chat 后台管理系统

## 🎯 项目简介

这是一个基于 Node.js + Express 开发的安全后台管理系统，用于管理 68Chat 前端单页网站的配置数据。

## ✨ 主要功能

### 🔧 配置管理
- 网站基本信息（标题、描述、关键词）
- 应用下载链接（Android、iOS、Windows、Mac）
- 统计代码配置（Google Analytics、自定义代码）
- 联系信息管理
- Favicon 文件上传

### 🔒 安全特性
- **自定义后台路径**：难以猜测的 URL（默认：`/admin-93874-control`）
- **用户认证**：用户名 + 密码登录，支持 bcrypt 哈希
- **JWT 会话管理**：安全的 Cookie 存储，HttpOnly + Secure
- **CSRF 防护**：防止跨站请求伪造攻击
- **防暴力破解**：登录失败5次锁定15分钟
- **二次验证**：修改配置需要验证码确认
- **请求验证**：验证 Content-Type 和 Origin
- **文件上传安全**：严格的文件类型和大小限制
- **操作日志**：记录所有管理操作

### 🎨 界面特色
- 响应式 Bootstrap 5 设计
- 现代化渐变配色
- 实时预览功能
- 友好的错误提示
- 自动保存提醒

## 🚀 快速开始

### 1. 环境要求
- Node.js 16.0 或更高版本
- npm 或 yarn 包管理器

### 2. 安装依赖
```bash
npm install
```

### 3. 环境配置
复制环境变量模板：
```bash
cp env.example .env
```

编辑 `.env` 文件，配置以下重要参数：
```env
# 服务器端口
PORT=3001

# 管理员账号（请修改默认值）
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password_here

# JWT 密钥（请生成随机字符串）
JWT_SECRET=your_super_secret_jwt_key_change_this_in_production

# 后台路径（请修改为难以猜测的路径）
ADMIN_PATH=/admin-93874-control

# Cookie 密钥
COOKIE_SECRET=your_cookie_secret_key_change_this
```

### 4. 启动服务
```bash
# 生产环境
npm start

# 开发环境（需要安装 nodemon）
npm run dev
```

### 5. 访问后台
- 前台页面：http://localhost:3001
- 后台管理：http://localhost:3001/admin-93874-control （根据你的 ADMIN_PATH 配置）

## 📁 项目结构

```
68chat-admin/
├── server.js                 # 主服务器文件
├── package.json              # 项目依赖配置
├── .env                      # 环境变量配置（需要创建）
├── env.example               # 环境变量模板
├── data.json                 # 网站配置数据
├── routes/
│   └── admin.js              # 后台管理路由
├── views/
│   ├── admin-login.ejs       # 登录页面模板
│   └── admin-panel.ejs       # 管理面板模板
├── logs/                     # 日志文件目录（自动创建）
│   ├── error.log
│   ├── combined.log
│   └── admin-operations.log
└── public/                   # 静态文件目录（自动创建）
    └── favicon.ico           # 上传的 favicon
```

## 🔐 安全配置指南

### 1. 密码安全
建议使用 bcrypt 哈希密码：
```bash
# 生成哈希密码
node -e "const bcrypt=require('bcryptjs'); console.log(bcrypt.hashSync('your_password', 12));"
```

### 2. JWT 密钥生成
```bash
# 生成随机密钥
node -e "console.log(require('crypto').randomBytes(64).toString('hex'));"
```

### 3. 后台路径自定义
修改 `.env` 中的 `ADMIN_PATH`：
```env
ADMIN_PATH=/your-custom-secret-path-here
```

### 4. 生产环境配置
```env
NODE_ENV=production
```

## 📊 功能说明

### 配置管理
- **网站信息**：标题、描述、关键词等 SEO 相关配置
- **下载链接**：各平台应用下载地址管理
- **统计代码**：Google Analytics 和自定义统计代码
- **联系信息**：邮箱和公司信息

### 文件上传
- **支持格式**：.ico、.png
- **大小限制**：100KB
- **安全检查**：文件类型和 MIME 类型双重验证

### 安全验证
- **登录保护**：5次失败锁定15分钟
- **操作验证**：修改配置需要验证码
- **会话管理**：24小时自动过期

## 🔧 API 接口

### 前端配置接口
```
GET /api/config
```
返回当前网站配置数据，供前端页面使用。

### 管理接口
所有管理接口都需要 JWT 认证：
- `GET /admin-path/login` - 登录页面
- `POST /admin-path/login` - 登录处理
- `GET /admin-path/panel` - 管理面板
- `POST /admin-path/update-config` - 更新配置
- `POST /admin-path/upload-favicon` - 上传 favicon
- `GET /admin-path/verification-code` - 获取验证码
- `POST /admin-path/logout` - 登出

## 📝 日志系统

系统会自动记录以下日志：
- **error.log**：错误日志
- **combined.log**：综合日志
- **admin-operations.log**：管理操作日志

日志格式为 JSON，包含时间戳、用户、IP 地址等信息。

## 🛡️ 安全最佳实践

1. **定期更换密钥**：JWT_SECRET 和 COOKIE_SECRET
2. **使用 HTTPS**：生产环境必须启用 SSL
3. **定期备份**：备份 data.json 和日志文件
4. **监控日志**：定期检查异常登录和操作
5. **更新依赖**：定期更新 npm 依赖包
6. **防火墙配置**：限制管理端口访问

## 🚨 故障排除

### 常见问题

1. **无法启动服务**
   - 检查端口是否被占用
   - 确认 `.env` 文件配置正确

2. **登录失败**
   - 检查用户名密码是否正确
   - 确认是否被锁定（等待15分钟）

3. **文件上传失败**
   - 检查文件格式和大小
   - 确认 public 目录权限

4. **配置保存失败**
   - 检查 data.json 文件权限
   - 确认磁盘空间充足

### 日志查看
```bash
# 查看错误日志
tail -f logs/error.log

# 查看管理操作日志
tail -f logs/admin-operations.log
```

## 📞 技术支持

如有问题，请查看：
1. 日志文件中的错误信息
2. 控制台输出的调试信息
3. 网络请求的响应状态

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

**⚠️ 重要提醒**：
- 生产环境部署前请务必修改所有默认密码和密钥
- 建议使用反向代理（如 Nginx）处理 SSL 和静态文件
- 定期备份配置数据和日志文件
