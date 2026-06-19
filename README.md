# 应急中心 · 心理测评系统

基于 Flask + PostgreSQL（兼容 SQLite）的心理测评系统，包含用户登录认证、测评系统、后台用户管理等功能。

## 功能特性

### 🔐 用户认证
- 用户名 + 密码登录
- Session 会话认证（2小时自动过期）
- 密码哈希存储（Werkzeug security）
- 未登录自动重定向到登录页

### 📋 心理测评系统
- **新入职人员测评**：大五人格、感知压力、应对方式、井控胜任力
- **在岗人员筛查**：职业倦怠、心理应激、安全心理状态
- **重大险情后创伤测评**：创伤后应激反应评估、PTSD临床筛查
- 答题进度实时保存
- 结果自动统计与可视化
- 支持打印和导出Word文档

### 👥 后台管理（管理员专属）
- 用户列表查看
- 新增用户（支持设置管理员权限）
- 修改用户密码
- 删除用户（保护默认管理员和当前登录用户）
- 用户统计概览

## 技术栈

- **后端框架**：Flask 3.0
- **数据库**：PostgreSQL（生产环境）/ SQLite（本地开发，自动兼容）
- **密码加密**：Werkzeug Security
- **前端**：原生 HTML + CSS + JavaScript
- **认证方式**：Session 会话认证
- **部署平台**：Render（推荐）

## 项目结构

```
psychological_assessment_system/
├── app.py                 # Flask 主程序
├── requirements.txt       # Python 依赖
├── README.md             # 部署说明
├── templates/            # 页面模板
│   ├── login.html        # 登录页
│   ├── admin.html        # 后台管理页
│   └── assessment.html   # 测评系统页
└── static/               # 静态资源（预留目录）
    ├── css/
    └── js/
```

## 快速开始（本地开发）

### 环境要求
- Python 3.8 或更高版本
- Windows / Linux / macOS 均可运行

### 安装步骤

#### 1. 解压项目
将压缩包解压到任意目录。

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

如果下载速度慢，可以使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3. 启动系统
```bash
python app.py
```

启动成功后会显示：
```
==================================================
  心理测评系统启动成功
  数据库类型: SQLite
  访问地址: http://127.0.0.1:5000
  默认管理员: admin / admin123
==================================================
```

> 💡 **说明**：本地运行默认使用 SQLite 数据库，无需额外配置。

#### 4. 访问系统
打开浏览器访问：**http://127.0.0.1:5000**

### 默认账号

| 用户名 | 密码 | 权限 |
|--------|------|------|
| admin | admin123 | 管理员 |

> ⚠️ **重要**：首次登录后请立即修改管理员密码！

---

## 部署到 Render（推荐）

### 第一步：准备代码

1. 在 GitHub 上新建一个仓库（如 `psychological-assessment`）
2. 将项目所有文件上传到仓库根目录

### 第二步：创建 PostgreSQL 数据库

1. 登录 [Render](https://render.com)
2. 点击 **"New +"** → 选择 **"PostgreSQL"**
3. 填写配置：
   - **Name**: `psychological-assessment-db`（随便起）
   - **Region**: Singapore（新加坡，离中国近）
   - **PostgreSQL Version**: 16
   - **Plan**: Free（免费版，90天有效期）
4. 点击 **"Create Database"** 创建
5. 创建完成后，复制 **"Internal Database URL"**（格式：`postgresql://xxx:xxx@xxx:5432/xxx`）

### 第三步：创建 Web Service

1. 点击 **"New +"** → 选择 **"Web Service"**
2. 连接你的 GitHub 账号，选择刚才的仓库
3. 填写配置：

| 配置项 | 填写内容 |
|--------|---------|
| **Name** | `psychological-assessment`（会成为你的子域名） |
| **Region** | Singapore（新加坡） |
| **Branch** | `main` 或 `master` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| **Plan** | Free（免费版） |

4. 点击 **"Advanced"** → 点击 **"Add Environment Variable"**
   - **Key**: `DATABASE_URL`
   - **Value**: 粘贴刚才复制的 PostgreSQL Internal Database URL

5. （可选）再添加一个环境变量增强安全性：
   - **Key**: `SECRET_KEY`
   - **Value**: 随便输入一串随机字符（如 `your-secret-key-here-2024`）

6. 点击 **"Create Web Service"** 开始部署

### 第四步：等待部署完成

- 部署过程大约需要 2-3 分钟
- 看到绿色的 **"Live"** 标志就表示成功了
- 点击上方的网址即可访问（格式：`https://你的项目名.onrender.com`）
- 使用默认账号 `admin` / `admin123` 登录

### Render 免费版限制

| 限制项 | 说明 |
|--------|------|
| **休眠时间** | 15分钟无访问自动休眠，下次访问需等待几十秒唤醒 |
| **PostgreSQL有效期** | 免费版90天，之后需升级付费版 |
| **每月时长** | 每月750小时运行时长（免费版足够用） |
| **数据持久化** | PostgreSQL 数据永久保存，不会因部署丢失 |

---

## 使用说明

### 管理员操作

1. **登录**：使用 admin 账号登录
2. **后台管理**：登录后自动进入后台管理页面
3. **新增用户**：在右侧"新增用户"表单填写用户名和密码，可选择是否设为管理员
4. **修改密码**：点击用户列表中的"改密码"按钮
5. **删除用户**：点击"删除"按钮（默认管理员和当前登录用户不可删除）
6. **进入测评**：点击顶部"测评系统"按钮进入测评页面

### 普通用户操作

1. **登录**：使用管理员分配的账号登录
2. **进行测评**：选择测评类型，按步骤完成答题
3. **查看结果**：完成后自动生成测评报告
4. **导出/打印**：支持导出Word文档或直接打印

---

## 安全说明

1. **密码安全**：所有密码均使用 SHA-256 哈希存储，无法逆向解密
2. **会话安全**：Session 2小时自动过期，退出登录立即失效
3. **权限隔离**：普通用户无法访问后台管理页面
4. **数据安全**：用户数据存储在 PostgreSQL 数据库，建议定期备份
5. **密钥安全**：生产环境请务必设置自定义的 SECRET_KEY 环境变量

---

## 常见问题

### Q: 忘记管理员密码怎么办？
A: 连接 PostgreSQL 数据库，删除 users 表中的 admin 用户，重启服务后会自动创建默认管理员账号（admin/admin123）。

### Q: 如何修改端口号？
A: 本地运行可设置环境变量 `PORT`，或编辑 `app.py` 最后一行的默认端口。

### Q: 如何修改 Session 过期时间？
A: 编辑 `app.py` 中的 `app.permanent_session_lifetime = timedelta(hours=2)`。

### Q: 支持多用户同时使用吗？
A: 支持，系统基于 Session 实现多用户隔离。

### Q: Render 免费版休眠后访问很慢怎么办？
A: 这是正常现象，升级到付费版（$7/月起）可取消休眠限制。

### Q: PostgreSQL 免费版90天后怎么办？
A: 升级到 Render 的付费 PostgreSQL 计划，或迁移到其他数据库服务。

---

## 技术支持

如有问题请联系系统管理员。

---

© 2024 应急中心 · 心理测评系统
