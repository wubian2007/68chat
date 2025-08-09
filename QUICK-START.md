# 68Chat 后台管理系统 - 快速启动指南

## 🚀 一键启动

### 方式1：使用启动脚本（推荐）
```bash
./start-admin.sh
```

### 方式2：手动启动
```bash
# 1. 安装依赖
npm install

# 2. 配置环境变量
cp config-demo.env .env

# 3. 启动服务
npm start
```

## 🔑 默认登录信息

- **后台地址**: http://localhost:3001/admin-93874-control
- **用户名**: admin
- **密码**: admin123456

⚠️ **重要**: 首次登录后请立即修改默认密码！

## 📱 功能演示

### 1. 登录系统
1. 访问后台地址
2. 输入默认用户名密码
3. 系统会显示管理面板

### 2. 配置管理
- **网站信息**: 修改标题、描述、关键词
- **下载链接**: 更新各平台下载地址
- **统计代码**: 配置 Google Analytics 等
- **联系信息**: 修改邮箱和公司信息

### 3. 文件上传
- 支持 .ico 和 .png 格式的 favicon
- 自动大小和格式验证
- 实时预览功能

### 4. 安全功能
- 登录失败5次自动锁定15分钟
- 配置修改需要验证码确认
- 完整的操作日志记录

## 🔧 自定义配置

编辑 `.env` 文件修改以下配置：

```env
# 修改端口
PORT=3001

# 修改管理员账号
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_secure_password

# 修改后台路径（安全）
ADMIN_PATH=/your-secret-admin-path

# 修改JWT密钥（安全）
JWT_SECRET=your_random_jwt_secret_key
```

## 📊 测试数据

系统包含完整的测试数据：
- 网站配置信息
- 下载链接示例
- 联系信息模板

## 🔒 生产环境部署

1. **修改所有默认配置**:
   ```bash
   # 生成安全的JWT密钥
   node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
   
   # 生成密码哈希
   node -e "const bcrypt=require('bcryptjs'); console.log(bcrypt.hashSync('your_password', 12))"
   ```

2. **设置生产环境**:
   ```env
   NODE_ENV=production
   ```

3. **配置反向代理** (推荐使用 Nginx)

4. **启用 HTTPS**

## 🛠️ 故障排除

### 端口被占用
```bash
# 查看端口占用
lsof -i :3001

# 杀死进程
kill -9 PID
```

### 权限问题
```bash
# 给予脚本执行权限
chmod +x start-admin.sh

# 检查文件权限
ls -la
```

### 依赖安装失败
```bash
# 清除缓存重新安装
rm -rf node_modules package-lock.json
npm install
```

## 📞 技术支持

- 查看日志: `tail -f logs/error.log`
- 检查配置: `cat .env`
- 测试连接: `curl http://localhost:3001`

## 🎯 功能特色

- ✅ 完整的安全认证系统
- ✅ 美观的 Bootstrap 5 界面
- ✅ 实时配置预览
- ✅ 文件上传管理
- ✅ 操作日志记录
- ✅ 防暴力破解保护
- ✅ CSRF 攻击防护
- ✅ 输入数据验证
- ✅ 响应式设计
- ✅ 一键部署脚本

---

🎉 **恭喜！您的 68Chat 后台管理系统已经准备就绪！**
