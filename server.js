const express = require('express');
const path = require('path');
const dotenv = require('dotenv');
const cookieParser = require('cookie-parser');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const winston = require('winston');

// 加载环境变量
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// 配置日志系统
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: '68chat-admin' },
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
    new winston.transports.File({ filename: 'logs/admin-operations.log', level: 'info' })
  ]
});

// 开发环境下也输出到控制台
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

// 创建logs目录
const fs = require('fs');
if (!fs.existsSync('logs')) {
  fs.mkdirSync('logs');
}

// 安全中间件
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
      scriptSrc: ["'self'", "https://cdn.jsdelivr.net"],
      imgSrc: ["'self'", "data:", "https:"],
      fontSrc: ["'self'", "https://cdn.jsdelivr.net"]
    }
  }
}));

// CORS 配置
app.use(cors({
  origin: function(origin, callback) {
    // 允许同源请求
    if (!origin) return callback(null, true);
    
    const allowedOrigins = [
      'http://localhost:3001',
      'http://localhost:8080',
      'http://localhost:8081'
    ];
    
    if (allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true
}));

// 基础中间件
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));
app.use(cookieParser(process.env.COOKIE_SECRET));

// 设置视图引擎
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// 静态文件服务
app.use(express.static(path.join(__dirname, 'public')));
app.use('/68tt_static', express.static(path.join(__dirname, '68tt_static')));

// 全局速率限制
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 1000, // 限制每个IP最多1000个请求
  message: {
    error: '请求过于频繁，请稍后再试'
  },
  standardHeaders: true,
  legacyHeaders: false
});

app.use(globalLimiter);

// 登录速率限制
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 5, // 最多5次登录尝试
  skipSuccessfulRequests: true,
  message: {
    error: '登录尝试过于频繁，请15分钟后再试'
  }
});

// 日志中间件
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.url}`, {
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    timestamp: new Date().toISOString()
  });
  next();
});

// 主页路由 - 服务前端页面
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/about.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'about.html'));
});

app.get('/privacy.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'privacy.html'));
});

app.get('/enterprise.html', (req, res) => {
  res.sendFile(path.join(__dirname, 'enterprise.html'));
});

// API路由 - 提供配置数据
app.get('/api/config', (req, res) => {
  try {
    const configPath = path.join(__dirname, 'data.json');
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    res.json(config);
  } catch (error) {
    logger.error('读取配置文件失败', error);
    res.status(500).json({ error: '配置加载失败' });
  }
});

// 后台管理路由
const adminRoutes = require('./routes/admin');
app.use(process.env.ADMIN_PATH || '/admin-93874-control', loginLimiter, adminRoutes);

// 404处理
app.use((req, res) => {
  res.status(404).json({ error: '页面不存在' });
});

// 错误处理中间件
app.use((error, req, res, next) => {
  logger.error('服务器错误', {
    error: error.message,
    stack: error.stack,
    url: req.url,
    method: req.method,
    ip: req.ip
  });

  if (error.code === 'EBADCSRFTOKEN') {
    res.status(403).json({ error: 'CSRF token 无效' });
  } else if (error.type === 'entity.too.large') {
    res.status(413).json({ error: '请求数据过大' });
  } else {
    res.status(500).json({ error: '服务器内部错误' });
  }
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`🚀 服务器运行在 http://localhost:${PORT}`);
  console.log(`📊 后台管理地址: http://localhost:${PORT}${process.env.ADMIN_PATH || '/admin-93874-control'}`);
  
  logger.info('服务器启动成功', {
    port: PORT,
    adminPath: process.env.ADMIN_PATH || '/admin-93874-control',
    nodeEnv: process.env.NODE_ENV || 'development'
  });
});

// 优雅关闭
process.on('SIGTERM', () => {
  logger.info('收到 SIGTERM 信号，正在关闭服务器...');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('收到 SIGINT 信号，正在关闭服务器...');
  process.exit(0);
});

module.exports = app;
