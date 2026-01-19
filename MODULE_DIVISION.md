# 项目模块分工（按代码模块）

## 项目模块总览

| 模块类别 | 文件/目录 | 功能描述 |
|---------|----------|---------|
| **后端核心** | `app/main.py` | FastAPI应用、路由、业务逻辑 |
| **认证模块** | `app/jwt_plugin.py` | JWT生成、验证、proof机制 |
| **配置模块** | `app/config.py` | 配置JSON生成 |
| **环境变量** | `app/properties.py` | 环境变量解析与默认值 |
| **前端页面** | `frontend/` | HTML页面（4个页面） |
| **静态资源** | `static/` | JavaScript、CSS |
| **数据库脚本** | `scripts/` | 数据库初始化、CTF数据重置 |
| **Docker部署** | `docker_scripts/`, `Dockerfile` | 容器化配置与部署脚本 |

---

## 详细模块分工

### **Zhenghan PEI (Team Leader)** - 项目架构与部署

#### 负责模块：

1. **项目整体架构设计**
   - 项目结构规划
   - CTF模式强制启用机制
   - 依赖层漏洞注入设计

2. **Docker 部署模块**
   - `Dockerfile` - 容器镜像构建
   - `docker_scripts/bootstrap_db.sh` - 构建时数据库初始化
   - `docker_scripts/docker-entrypoint.sh` - 运行时入口点
   - 容器化部署流程设计

3. **配置管理模块**
   - `app/config.py` - 配置JSON生成与导出
   - `app/properties.py` - 环境变量管理
   - 运行时配置与构建时配置的区分

4. **项目文档**
   - `README.md` - 项目文档
   - `PROJECT_REPORT.md` / `PROJECT_REPORT_CN.md` - 项目报告

#### 核心代码文件：
- `Dockerfile`
- `docker_scripts/bootstrap_db.sh`
- `docker_scripts/docker-entrypoint.sh`
- `app/config.py`
- `app/properties.py`
- `README.md`

#### 负责的API端点：
- 无（主要负责基础设施）

#### 技术重点：
- Docker容器化
- 数据库初始化流程
- 环境变量配置管理
- 项目文档编写

---

### **Haihang WANG** - 后端核心与数据库

#### 负责模块：

1. **FastAPI 应用核心**
   - `app/main.py` 中的核心架构部分
   - `get_conn()` 函数 - 数据库连接管理
   - CTF模式检测与漏洞注入机制

2. **数据库模块**
   - `scripts/db_bootstrap.py` - 数据库初始化
   - `scripts/init_prod.sql` - 生产环境数据库架构
   - `scripts/reset_ctf.sql` - CTF数据重置
   - `scripts/run_init_prod.py` - 初始化脚本运行器
   - `scripts/run_reset_ctf.py` - CTF重置脚本运行器

3. **清理函数设计**
   - `app/main.py` 中的 `sanitize_email()` 函数
   - `app/main.py` 中的 `sanitize_admin()` 函数
   - 部分清理机制的设计与实现

4. **公共API端点**
   - `GET /api/home` - 首页数据API（信息泄露点）

#### 核心代码文件：
- `app/main.py` (部分：架构、连接管理、清理函数、公共API)
- `scripts/db_bootstrap.py`
- `scripts/init_prod.sql`
- `scripts/reset_ctf.sql`
- `scripts/run_init_prod.py`
- `scripts/run_reset_ctf.py`

#### 负责的API端点：
- `GET /api/home` - 获取首页文章列表（包含邮箱泄露）

#### 技术重点：
- 数据库连接管理
- 依赖层漏洞注入机制
- SQL清理函数设计
- 数据库架构设计

---

### **Peipei LU** - 用户功能与前端

#### 负责模块：

1. **用户认证功能**
   - `app/main.py` 中的用户登录API
   - `POST /api/login/user` - 用户登录端点
   - 用户JWT生成流程

2. **用户相关前端页面**
   - `frontend/index.html` - 首页
   - `frontend/personal_space.html` - 用户个人空间页面
   - `frontend/admin_login.html` - 管理员登录页面（前端部分）

3. **用户相关API**
   - `GET /api/user/{username}` - 获取用户文章
   - `POST /api/user/answer/{jwt}` - 用户旗帜提交
   - `GET /personal_space` - 个人空间页面路由

4. **前端静态资源**
   - `static/app.js` - 前端JavaScript（用户相关功能）
   - `static/style.css` - 样式表

5. **HTML路由**
   - `GET /` - 首页路由
   - `GET /personal_space` - 个人空间路由

#### 核心代码文件：
- `app/main.py` (部分：用户登录、用户API、用户相关路由)
- `frontend/index.html`
- `frontend/personal_space.html`
- `frontend/admin_login.html`
- `static/app.js` (用户相关部分)
- `static/style.css`

#### 负责的API端点：
- `GET /` - 首页
- `GET /personal_space` - 个人空间页面
- `POST /api/login/user` - 用户登录
- `GET /api/user/{username}` - 获取用户数据
- `POST /api/user/answer/{jwt}` - 用户旗帜提交

#### 技术重点：
- 用户认证流程
- SQL注入漏洞（用户登录）
- 前端与后端交互
- HTML/CSS/JavaScript开发

---

### **Dongshan ZHU** - 管理员功能与CTF

#### 负责模块：

1. **管理员认证功能**
   - `app/main.py` 中的管理员登录API
   - `POST /api/login/admin` - 管理员登录端点
   - 管理员JWT生成流程

2. **管理员相关前端页面**
   - `frontend/admin.html` - 管理员面板页面

3. **管理员相关API**
   - `GET /api/admin/check` - 管理员JWT验证
   - `POST /api/admin/answer/{jwt}` - 管理员旗帜提交
   - `GET {ADMIN_URL}` - 管理员面板路由（默认 `/admin123`）
   - `GET {ADMIN_LOGIN_URL}` - 管理员登录页面路由（默认 `/admin456_login`）

4. **CTF功能模块**
   - `app/main.py` 中的CTF进度跟踪
   - `GET /api/flags` - CTF旗帜状态查询
   - CTF进度数据库更新逻辑

5. **JWT认证模块**
   - `app/jwt_plugin.py` - JWT生成与验证
   - 用户和管理员的JWT实现
   - Proof机制实现

#### 核心代码文件：
- `app/main.py` (部分：管理员登录、管理员API、CTF功能、管理员路由)
- `app/jwt_plugin.py` - JWT认证核心
- `frontend/admin.html` - 管理员面板

#### 负责的API端点：
- `GET {ADMIN_URL}` - 管理员面板（默认 `/admin123`）
- `GET {ADMIN_LOGIN_URL}` - 管理员登录页面（默认 `/admin456_login`）
- `POST /api/login/admin` - 管理员登录
- `GET /api/admin/check` - 验证管理员JWT
- `POST /api/admin/answer/{jwt}` - 管理员旗帜提交
- `GET /api/flags` - CTF进度查询

#### 技术重点：
- 管理员认证流程
- SQL注入漏洞（管理员登录，更复杂）
- JWT实现与验证
- CTF机制设计
- 隐藏URL设计

---

## 模块依赖关系

```
Zhenghan (部署/配置)
    ↓
Haihang (数据库/核心架构)
    ↓
Peipei (用户功能) ←→ Dongshan (管理员功能)
    ↓                    ↓
    前端页面与API集成
```

## 代码统计

### Zhenghan PEI
- **主要文件数：** 6个
- **代码行数：** ~500行
- **重点：** 基础设施、部署、配置

### Haihang WANG
- **主要文件数：** 6个
- **代码行数：** ~800行
- **重点：** 后端核心、数据库、清理机制

### Peipei LU
- **主要文件数：** 5个
- **代码行数：** ~600行
- **重点：** 用户功能、前端页面

### Dongshan ZHU
- **主要文件数：** 3个
- **代码行数：** ~700行
- **重点：** 管理员功能、JWT、CTF机制

---

## 回答老师问题的模板

### 如果老师问："你负责哪些模块？"

#### **Zhenghan PEI 回答：**
"我主要负责项目的架构设计和Docker部署模块。具体包括：
1. Docker容器化配置（Dockerfile和部署脚本）
2. 数据库初始化流程（bootstrap脚本）
3. 配置管理模块（环境变量和配置JSON）
4. 项目文档编写

我设计了CTF模式强制启用的机制，确保漏洞行为在依赖层注入，同时保持业务逻辑的干净。"

#### **Haihang WANG 回答：**
"我负责后端核心架构和数据库模块。具体包括：
1. FastAPI应用的核心架构（get_conn函数和连接管理）
2. 数据库模块（初始化脚本和架构设计）
3. SQL清理函数（sanitize_email和sanitize_admin）
4. 公共API端点（/api/home，包含信息泄露点）

我实现了依赖层漏洞注入机制，这是项目的核心设计理念。"

#### **Peipei LU 回答：**
"我负责用户功能模块和前端页面。具体包括：
1. 用户认证功能（/api/login/user端点）
2. 用户相关前端页面（首页、个人空间、登录页面）
3. 用户API（获取用户数据、提交用户旗帜）
4. 前端静态资源（JavaScript和CSS）

我实现了用户登录的SQL注入漏洞，并开发了相应的前端界面。"

#### **Dongshan ZHU 回答：**
"我负责管理员功能和CTF机制。具体包括：
1. 管理员认证功能（/api/login/admin端点）
2. JWT认证模块（jwt_plugin.py，用户和管理员的JWT实现）
3. 管理员前端页面（admin.html）
4. CTF功能模块（旗帜提交和进度跟踪）

我实现了更复杂的管理员SQL注入漏洞，并设计了完整的JWT认证系统和CTF机制。"

---

## 模块协作说明

### 模块间接口：

1. **Zhenghan → Haihang：**
   - 提供环境变量配置（properties.py）
   - 提供数据库初始化流程

2. **Haihang → Peipei/Dongshan：**
   - 提供 `get_conn()` 函数
   - 提供清理函数（sanitize_email, sanitize_admin）
   - 提供数据库连接

3. **Peipei ↔ Dongshan：**
   - 共享前端静态资源（app.js, style.css）
   - 共享JWT验证逻辑（Dongshan实现，Peipei使用）

4. **Dongshan → 所有人：**
   - 提供JWT生成和验证功能（jwt_plugin.py）

---

## 关键技术点分配

| 技术点 | 负责人 | 说明 |
|--------|--------|------|
| Docker容器化 | Zhenghan | 完整的容器化方案 |
| 依赖层漏洞注入 | Haihang | 核心安全机制 |
| SQL清理函数 | Haihang | 部分清理机制设计 |
| 用户SQL注入 | Peipei | 用户登录漏洞 |
| 管理员SQL注入 | Dongshan | 更复杂的注入漏洞 |
| JWT实现 | Dongshan | 完整的认证系统 |
| 前端开发 | Peipei | HTML/CSS/JS |
| CTF机制 | Dongshan | 旗帜提交与跟踪 |
| 数据库设计 | Haihang | 架构与初始化 |
| 配置管理 | Zhenghan | 环境变量与配置 |

---

## 代码审查重点

### 每个成员需要能回答的问题：

#### Zhenghan：
- Docker构建流程是如何工作的？
- 为什么数据库配置不能在运行时修改？
- CTF模式是如何强制启用的？

#### Haihang：
- `get_conn()` 函数如何注入漏洞？
- 清理函数的设计原理是什么？
- 为什么部分清理是危险的？

#### Peipei：
- 用户登录的SQL注入是如何工作的？
- 前端如何与后端API交互？
- 信息泄露是如何实现的？

#### Dongshan：
- 管理员登录的SQL注入为什么更复杂？
- JWT的proof机制是如何工作的？
- CTF旗帜提交的流程是什么？
