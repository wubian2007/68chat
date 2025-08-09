const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const csrf = require('csurf');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { body, validationResult } = require('express-validator');
const winston = require('winston');

const router = express.Router();

// 配置日志
const adminLogger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/admin-operations.log' })
  ]
});

// CSRF 保护
const csrfProtection = csrf({ cookie: true });

// 登录失败计数器 (生产环境应使用Redis或数据库)
const loginAttempts = new Map();

// 文件上传配置
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadPath = path.join(__dirname, '..', 'public');
    if (!fs.existsSync(uploadPath)) {
      fs.mkdirSync(uploadPath, { recursive: true });
    }
    cb(null, uploadPath);
  },
  filename: function (req, file, cb) {
    // 保持原文件名，但确保是favicon
    const ext = path.extname(file.originalname).toLowerCase();
    if (ext === '.ico') {
      cb(null, 'favicon.ico');
    } else if (ext === '.png') {
      cb(null, 'favicon.png');
    } else {
      cb(new Error('不支持的文件类型'));
    }
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: parseInt(process.env.MAX_FILE_SIZE) || 102400 // 100KB
  },
  fileFilter: function (req, file, cb) {
    const allowedTypes = /ico|png/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('只允许上传 .ico 和 .png 格式的文件'));
    }
  }
});

// JWT 验证中间件
const verifyToken = (req, res, next) => {
  const token = req.cookies.adminToken;

  if (!token) {
    return res.status(401).redirect('./login');
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    res.clearCookie('adminToken');
    return res.status(401).redirect('./login');
  }
};

// 验证管理员密码的工具函数
const verifyAdminPassword = async (username, password) => {
  const adminUsername = process.env.ADMIN_USERNAME;
  const adminPassword = process.env.ADMIN_PASSWORD;

  if (username !== adminUsername) {
    return false;
  }

  // 如果密码已经是哈希值，直接比较；否则进行哈希比较
  if (adminPassword.startsWith('$2a$') || adminPassword.startsWith('$2b$')) {
    return await bcrypt.compare(password, adminPassword);
  } else {
    // 对于明文密码，先哈希再比较（不推荐生产环境使用）
    return password === adminPassword;
  }
};

// 检查登录失败次数
const checkLoginAttempts = (ip) => {
  const attempts = loginAttempts.get(ip) || { count: 0, lastAttempt: 0 };
  const now = Date.now();
  const lockoutTime = parseInt(process.env.LOCKOUT_TIME) || 900000; // 15分钟

  // 如果在锁定期内
  if (attempts.count >= 5 && (now - attempts.lastAttempt) < lockoutTime) {
    return false;
  }

  // 如果锁定期已过，重置计数
  if ((now - attempts.lastAttempt) > lockoutTime) {
    loginAttempts.delete(ip);
  }

  return true;
};

// 记录登录失败
const recordLoginFailure = (ip) => {
  const attempts = loginAttempts.get(ip) || { count: 0, lastAttempt: 0 };
  attempts.count += 1;
  attempts.lastAttempt = Date.now();
  loginAttempts.set(ip, attempts);
};

// 清除登录失败记录
const clearLoginFailures = (ip) => {
  loginAttempts.delete(ip);
};

// 登录页面
router.get('/login', csrfProtection, (req, res) => {
  res.render('admin-login', {
    csrfToken: req.csrfToken(),
    error: null
  });
});

// 登录处理
router.post('/login', csrfProtection, [
  body('username').trim().isLength({ min: 1 }).withMessage('用户名不能为空'),
  body('password').isLength({ min: 1 }).withMessage('密码不能为空')
], async (req, res) => {
  const errors = validationResult(req);
  const clientIP = req.ip;

  // 检查是否被锁定
  if (!checkLoginAttempts(clientIP)) {
    adminLogger.warn('登录被锁定', {
      ip: clientIP,
      timestamp: new Date().toISOString()
    });
    
    return res.render('admin-login', {
      csrfToken: req.csrfToken(),
      error: '登录失败次数过多，请15分钟后再试'
    });
  }

  if (!errors.isEmpty()) {
    recordLoginFailure(clientIP);
    return res.render('admin-login', {
      csrfToken: req.csrfToken(),
      error: '请填写完整的登录信息'
    });
  }

  const { username, password } = req.body;

  try {
    const isValid = await verifyAdminPassword(username, password);

    if (!isValid) {
      recordLoginFailure(clientIP);
      
      adminLogger.warn('登录失败', {
        username,
        ip: clientIP,
        timestamp: new Date().toISOString()
      });

      return res.render('admin-login', {
        csrfToken: req.csrfToken(),
        error: '用户名或密码错误'
      });
    }

    // 登录成功
    clearLoginFailures(clientIP);
    
    const token = jwt.sign(
      { username, loginTime: Date.now() },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.cookie('adminToken', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 24 * 60 * 60 * 1000 // 24小时
    });

    adminLogger.info('管理员登录成功', {
      username,
      ip: clientIP,
      timestamp: new Date().toISOString()
    });

    res.redirect('./panel');

  } catch (error) {
    adminLogger.error('登录处理错误', {
      error: error.message,
      ip: clientIP,
      timestamp: new Date().toISOString()
    });
    
    res.render('admin-login', {
      csrfToken: req.csrfToken(),
      error: '登录处理失败，请重试'
    });
  }
});

// 管理面板
router.get('/panel', verifyToken, csrfProtection, (req, res) => {
  try {
    const configPath = path.join(__dirname, '..', 'data.json');
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

    res.render('admin-panel', {
      csrfToken: req.csrfToken(),
      config: config,
      user: req.user,
      success: req.query.success,
      error: req.query.error
    });
  } catch (error) {
    adminLogger.error('读取配置失败', {
      error: error.message,
      user: req.user.username,
      timestamp: new Date().toISOString()
    });

    res.status(500).render('admin-panel', {
      csrfToken: req.csrfToken(),
      config: null,
      user: req.user,
      success: null,
      error: '配置加载失败'
    });
  }
});

// 更新配置
router.post('/update-config', verifyToken, csrfProtection, [
  body('site.title').trim().isLength({ min: 1, max: 100 }).withMessage('网站标题长度必须在1-100字符之间'),
  body('site.description').trim().isLength({ min: 1, max: 500 }).withMessage('网站描述长度必须在1-500字符之间'),
  body('site.keywords').trim().isLength({ max: 200 }).withMessage('关键词长度不能超过200字符'),
  body('downloads.android.url').isURL().withMessage('Android下载链接格式不正确'),
  body('downloads.ios.url').isURL().withMessage('iOS下载链接格式不正确'),
  body('downloads.windows.url').isURL().withMessage('Windows下载链接格式不正确'),
  body('downloads.mac.url').isURL().withMessage('Mac下载链接格式不正确'),
  body('contact.email').isEmail().withMessage('邮箱格式不正确'),
  body('verificationCode').trim().isLength({ min: 1 }).withMessage('验证码不能为空')
], (req, res) => {
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    return res.redirect('./panel?error=' + encodeURIComponent('输入数据验证失败：' + errors.array().map(e => e.msg).join(', ')));
  }

  // 简单的验证码检查（实际项目中应该使用更安全的方式）
  const { verificationCode } = req.body;
  const expectedCode = req.user.username.slice(-4) + Date.now().toString().slice(-2);
  
  if (verificationCode !== expectedCode.slice(-6)) {
    return res.redirect('./panel?error=' + encodeURIComponent('验证码错误'));
  }

  try {
    const configPath = path.join(__dirname, '..', 'data.json');
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

    // 更新配置
    const updatedConfig = {
      ...config,
      site: {
        ...config.site,
        title: req.body['site.title'],
        description: req.body['site.description'],
        keywords: req.body['site.keywords']
      },
      downloads: {
        android: {
          url: req.body['downloads.android.url'],
          version: req.body['downloads.android.version'] || config.downloads.android.version
        },
        ios: {
          url: req.body['downloads.ios.url'],
          version: req.body['downloads.ios.version'] || config.downloads.ios.version
        },
        windows: {
          url: req.body['downloads.windows.url'],
          version: req.body['downloads.windows.version'] || config.downloads.windows.version
        },
        mac: {
          url: req.body['downloads.mac.url'],
          version: req.body['downloads.mac.version'] || config.downloads.mac.version
        }
      },
      analytics: {
        google: {
          id: req.body['analytics.google.id'] || config.analytics.google.id,
          enabled: req.body['analytics.google.enabled'] === 'true'
        },
        custom: {
          code: req.body['analytics.custom.code'] || '',
          enabled: req.body['analytics.custom.enabled'] === 'true'
        }
      },
      contact: {
        email: req.body['contact.email'],
        company: req.body['contact.company'] || config.contact.company
      },
      lastModified: new Date().toISOString(),
      version: config.version
    };

    // 保存配置
    fs.writeFileSync(configPath, JSON.stringify(updatedConfig, null, 2));

    // 记录操作日志
    adminLogger.info('配置更新成功', {
      user: req.user.username,
      ip: req.ip,
      changes: {
        site: updatedConfig.site,
        downloads: updatedConfig.downloads,
        analytics: updatedConfig.analytics,
        contact: updatedConfig.contact
      },
      timestamp: new Date().toISOString()
    });

    res.redirect('./panel?success=' + encodeURIComponent('配置更新成功'));

  } catch (error) {
    adminLogger.error('配置更新失败', {
      error: error.message,
      user: req.user.username,
      ip: req.ip,
      timestamp: new Date().toISOString()
    });

    res.redirect('./panel?error=' + encodeURIComponent('配置保存失败：' + error.message));
  }
});

// 上传 favicon
router.post('/upload-favicon', verifyToken, csrfProtection, (req, res) => {
  upload.single('favicon')(req, res, function (err) {
    if (err) {
      adminLogger.error('文件上传失败', {
        error: err.message,
        user: req.user.username,
        ip: req.ip,
        timestamp: new Date().toISOString()
      });

      return res.redirect('./panel?error=' + encodeURIComponent('文件上传失败：' + err.message));
    }

    if (!req.file) {
      return res.redirect('./panel?error=' + encodeURIComponent('请选择要上传的文件'));
    }

    try {
      // 更新配置中的favicon路径
      const configPath = path.join(__dirname, '..', 'data.json');
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

      config.site.favicon = `public/${req.file.filename}`;
      config.lastModified = new Date().toISOString();

      fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

      adminLogger.info('Favicon上传成功', {
        user: req.user.username,
        ip: req.ip,
        filename: req.file.filename,
        size: req.file.size,
        timestamp: new Date().toISOString()
      });

      res.redirect('./panel?success=' + encodeURIComponent('Favicon上传成功'));

    } catch (error) {
      adminLogger.error('Favicon配置更新失败', {
        error: error.message,
        user: req.user.username,
        ip: req.ip,
        timestamp: new Date().toISOString()
      });

      res.redirect('./panel?error=' + encodeURIComponent('Favicon配置更新失败'));
    }
  });
});

// 生成验证码
router.get('/verification-code', verifyToken, (req, res) => {
  const code = req.user.username.slice(-4) + Date.now().toString().slice(-2);
  res.json({ code: code.slice(-6) });
});

// 预览前台页面
router.get('/preview', verifyToken, (req, res) => {
  res.redirect('/');
});

// 登出
router.post('/logout', verifyToken, (req, res) => {
  adminLogger.info('管理员登出', {
    user: req.user.username,
    ip: req.ip,
    timestamp: new Date().toISOString()
  });

  res.clearCookie('adminToken');
  res.redirect('./login');
});

// 默认重定向到登录页
router.get('/', (req, res) => {
  res.redirect('./login');
});

module.exports = router;
