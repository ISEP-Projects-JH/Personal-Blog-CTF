# PPT 详细讲稿内容

## 封面页 - Zhenghan PEI

**讲稿：**

大家好，我是 Zhenghan PEI，今天由我们团队为大家介绍 **Personal Blog CTF** 项目。

这是我们 Project 2 的作品，主题是"Unified Deployment & Design Guide"。

我们的团队成员包括：
- 我本人，Zhenghan PEI，作为团队负责人
- Haihang WANG
- Peipei LU  
- Dongshan ZHU

这是 II.3524 - Sécurité Logicielle 课程的第二个项目。

今天我们将展示一个专门设计的 SQL 注入 CTF 挑战，它演示了依赖层漏洞如何影响看似安全的应用程序。

---

## 第1页：Table of Contents - Zhenghan PEI

**讲稿：**

在开始之前，让我先概述一下今天的演讲结构。

我们将按照以下六个部分进行：

1. **Project Overview** - 项目概述，介绍项目的目标和核心理念
2. **Architecture & Design** - 技术架构与设计，展示系统如何构建
3. **CTF Challenges** - CTF 挑战详解，包括用户和管理员两个挑战
4. **Solution Walkthrough** - 解决方案详解，展示如何利用漏洞
5. **Demo** - 现场演示，实际操作展示攻击过程
6. **Conclusion** - 总结与要点，提炼关键安全教训

现在让我们从项目概述开始。

---

## 第2页：Project Overview - Zhenghan PEI

**讲稿：**

首先，让我介绍一下这个项目是什么。

**这个项目是什么？**

这是一个**自包含的、面向教学的 SQL 注入 CTF 服务**。它模拟了一个简化的"个人博客"应用程序，但专门设计用于安全教学。

**核心哲学：**

这个项目想要传达的核心思想是：**Clean Business Logic ≠ Secure Application**。

也就是说，即使应用程序的业务逻辑看起来完美无缺，如果底层的依赖——特别是数据库驱动层——存在缺陷或配置错误，整个应用仍然可能是脆弱的。

我们采用 **"Docker-First"** 设计理念，这意味着：
- 数据库状态在构建时冻结
- 可以完全重现的利用路径
- 确保每次运行都有一致的 CTF 环境

**目标受众：**

这个项目主要面向三类人群：
- **CTF 玩家** - 想要练习 SQL 注入技能的安全爱好者
- **安全学习者** - 想要理解依赖层安全问题的学生
- **挑战作者** - 想要创建类似教学工具的教育工作者

这个项目基于 CVE-2019-12989 的漏洞模式，展示了真实世界中依赖库可能引入的安全问题。

现在，让我把时间交给 Haihang，他将详细介绍系统的技术架构。

---

## 第3页：Architecture & Design - Haihang WANG

**讲稿：**

谢谢 Zhenghan。现在让我为大家展示系统的技术架构。

**系统架构流程：**

我们的系统采用分层架构，数据流如下：

首先，**Browser**（浏览器）发起请求。

请求到达 **FastAPI 应用层**，这里我们标记为 "Clean Logic"（干净的逻辑）。这意味着应用层的代码本身是安全的，使用了参数化查询。

然后，请求通过 **CTF SQL Driver**（CTF SQL 驱动层），这里标记为 "Injected Vuln"（注入的漏洞）。这是关键点——漏洞不是出现在应用代码中，而是在依赖层。

最后，数据到达 **MariaDB** 数据库。

**系统特征：**

我们的系统具有以下特征：

1. **Single Container** - 单容器部署，前端和后端运行在同一个容器中
2. **JWT Auth** - 使用 JWT 进行身份认证，区分普通用户和管理员
3. **Static Assets** - 静态资源（HTML、CSS、JavaScript）由 FastAPI 直接提供

**CTF 特性：**

为了确保 CTF 行为的一致性，我们做了两个关键设计：

1. **CTF Mode Enforced** - CTF 模式在启动时硬编码。我们在代码中使用 `builtins.CTF_MODE = "ctf"`，确保不会意外回退到生产安全模式。

2. **Partial Sanitization** - 部分清理机制在 helper 函数中实现，而不是在业务逻辑中。这样业务代码保持干净，但漏洞行为在连接层注入。

这种设计模拟了真实场景：即使开发者编写了看似安全的代码，如果使用的数据库驱动库存在缺陷，整个应用仍然可能被攻击。

---

## 第4页：The 'Hidden' Vulnerability - Haihang WANG

**讲稿：**

现在让我展示这个"隐藏"漏洞是如何工作的。

**业务逻辑（看起来安全）：**

在应用层，代码看起来非常安全：

```python
conn = get_conn(sanitize_email)
cur.execute("SELECT * FROM users WHERE email=%s", (email,))
```

这里：
- 使用了 `get_conn()` 函数，并传入了 `sanitize_email` 清理函数
- SQL 查询使用了参数化占位符 `%s`
- 从表面上看，这应该是安全的

**在 `get_conn` 内部（依赖层）：**

但是，当我们深入 `get_conn` 函数的实现：

```python
def get_conn(sanitizer):
    # 如果是 CTF 会话，注入漏洞行为
    return ctf_sql.MySql.connect(..., sanitizer=sanitizer)
```

关键点在于：
- 这个函数调用了 `ctf_sql.MySql.connect()`
- 即使传入了 `sanitizer`，在 CTF 模式下，这个驱动库可能会以不安全的方式处理输入
- 漏洞行为被注入到依赖层，而不是应用代码中

**关键洞察：**

这模拟了真实世界的场景，其中：
- 开发者可能编写了看起来安全的代码
- 但使用的第三方库（如 ORM 或数据库驱动）可能存在 bug 或配置错误
- 这些库级别的缺陷可能导致整个应用存在安全漏洞

这就是为什么安全审计不仅要检查应用代码，还要审查依赖库的行为。

现在，让我把时间交给 Peipei，她将详细介绍第一个 CTF 挑战。

---

## 第5页：Challenge Scope - Peipei LU

**讲稿：**

谢谢 Haihang。现在让我介绍我们的 CTF 挑战范围。

我们设计了两个独立的挑战，每个挑战都有不同的目标和约束：

**1. User Flag Challenge（用户旗帜挑战）**

- **目标（Objective）：** 以特定用户身份登录系统
- **约束（Constraint）：** 攻击点在于 Email 参数
- **防御（Defense）：** 系统阻止基本的 SQL 注入模式，如 'OR'、'1=1' 等

这个挑战相对简单，适合初学者理解 SQL 注入的基本原理。

**2. Admin Flag Challenge（管理员旗帜挑战）**

- **目标（Objective）：** 找到隐藏的管理员面板并成功登录
- **约束（Constraint）：** 需要发现隐藏的 URL，并且攻击点在于用户名参数
- **防御（Defense）：** 需要满足特定的字符串模式要求（至少 5 个拉丁字母）

这个挑战更加复杂，需要：
- 信息收集技能（找到隐藏的管理员登录页面）
- 高级 SQL 注入技术（绕过更严格的清理规则）
- 理解 MySQL 的特殊语法（如 `||` 运算符）

现在让我详细展示用户挑战的解决过程。

---

## 第6页：User Challenge: Reconnaissance - Peipei LU

**讲稿：**

用户挑战的第一步是**信息收集（Reconnaissance）**。

**Step 1: Information Gathering**

在真实的渗透测试中，信息收集是至关重要的第一步。在我们的挑战中，我们需要找到一个有效的目标邮箱地址。

我们检查公共 API 端点：`GET /api/home`

这个端点返回首页的博客文章列表。重要的是，**响应中故意泄露了作者邮箱**。这是设计中的信息泄露，模拟了真实世界中可能出现的配置错误。

**示例响应：**

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

**Target Acquired: alice@example.com**

通过这个 API，我们成功获取了目标用户的邮箱地址：`alice@example.com`。

这个邮箱将是我们 SQL 注入攻击的目标。注意，我们不需要猜测邮箱，因为系统故意暴露了这个信息。这强调了**信息泄露**在安全评估中的重要性。

现在，有了目标邮箱，我们可以进入下一步：构造 SQL 注入载荷。

---

## 第7页：User Challenge: Exploitation - Peipei LU

**讲稿：**

现在进入用户挑战的核心部分：**绕过清理机制（Bypassing Sanitization）**。

**Bypassing Sanitization Rules:**

首先，让我们了解系统的清理规则：

**被阻止的模式：**
- `'OR'` - 逻辑或运算符
- `'='` - 等号
- `'TRUE'` - 布尔值
- `'--'` - SQL 注释

**允许的模式：**
- `'AND'` - 逻辑与运算符
- `'()'` - 括号
- `'"'` - 引号

**The Payload:**

基于这些规则，我们构造了一个载荷，使查询有效而无需知道密码：

```
alice@example.com' AND ('1') #
```

让我解释这个载荷的构造：
- `alice@example.com` - 我们知道的目标邮箱
- `'` - 闭合原始查询中的引号
- ` AND ('1')` - 添加一个总是为真的条件（`'1'` 在 SQL 中为真）
- `#` - MySQL 注释符，注释掉后续的密码检查

**Resulting Query:**

当这个载荷被注入后，实际的 SQL 查询变成：

```sql
SELECT id FROM users
WHERE email = 'alice@example.com' AND ('1') #' AND pass=...
```

**关键点：**

`#` 符号注释掉了 `' AND pass=...` 部分，这意味着：
- 我们绕过了密码验证
- 只要邮箱匹配，查询就会成功
- 我们不需要知道真实的密码

这就是为什么**部分清理是危险的**。即使系统阻止了一些明显的 SQL 注入模式，攻击者仍然可以通过组合允许的字符来构造有效的载荷。

现在，让我把时间交给 Dongshan，他将展示更复杂的管理员挑战。

---

## 第8页：Admin Challenge: Reconnaissance - Dongshan ZHU

**讲稿：**

谢谢 Peipei。现在让我介绍管理员挑战，这是一个更高级的挑战。

**Step 1: Finding the Admin Panel**

管理员挑战的第一步是**找到隐藏的管理员登录页面**。

**挑战：**

与用户登录不同，管理员登录页面的 URL **没有在首页上链接**。这意味着：
- 你不能通过点击链接找到它
- 需要主动发现这个隐藏的端点

**配置方式：**

管理员登录 URL 通过环境变量 `ADMIN_LOGIN_URL` 配置，默认值是 `/admin456_login`。

**发现方法：**

在真实的渗透测试中，有几种方法可以发现隐藏的端点：

1. **模糊测试（Fuzzing）** - 尝试常见的路径，如 `/admin`、`/admin_login`、`/admin456_login` 等
2. **检查配置文件** - 如果 `config.json` 暴露，可能包含 URL 信息
3. **目录扫描工具** - 使用工具如 dirb、gobuster 等

在我们的 CTF 中，为了教学目的，这个 URL 是已知的，但在真实场景中，发现隐藏端点是攻击链中的关键步骤。

一旦找到了管理员登录页面，我们就可以进入下一步：构造 SQL 注入载荷。

---

## 第9页：Admin Challenge: Exploitation - Dongshan ZHU

**讲稿：**

管理员挑战的第二步是**高级 SQL 注入（Advanced SQLi）**。

**Step 2: Advanced SQLi**

这个挑战比用户挑战更复杂，因为清理规则更加严格。

**约束：**

清理器有一个特殊要求：**在第一个引号之前必须至少 5 个拉丁字母**。

这意味着：
- 不能直接使用 `'` 来闭合引号
- 必须在引号前有足够的字母来满足模式匹配

**目标：** 用户名字段

**The Payload:**

基于这些约束，我们构造的载荷是：

```
admin' || ('1')#
```

让我详细解释这个载荷：

**Payload 解释：**

1. **`"admin"`** - 这 5 个字母满足"至少 5 个拉丁字母"的要求
2. **`'`** - 现在可以安全地闭合引号
3. **`||`** - 这是 MySQL 的逻辑 OR 运算符（在 ANSI 模式下）
4. **`('1')`** - 一个总是为真的条件
5. **`#`** - 注释掉后续的密码检查

**为什么使用 `||` 而不是 `OR`？**

因为标准的 `'OR'` 关键字被清理器阻止了。但是 `||` 是 MySQL 支持的另一种逻辑 OR 写法，在某些配置下与 `OR` 等价。

这展示了：
- 理解数据库特定语法的重要性
- 绕过清理规则需要创造性思维
- 部分清理往往存在可被利用的漏洞

现在，让我通过现场演示来展示这些攻击的实际操作。

---

## 第10页：Live Demo - Dongshan ZHU

**讲稿：**

现在进入 **DEMO TIME**，我将现场演示整个攻击过程。演示时间最多 5 分钟。

**演示步骤：**

**步骤 1：部署 Docker 容器**

```bash
docker run -p 8000:8000 personal-blog-ctf
```

容器启动后，服务将在 `http://localhost:8000` 运行。

**步骤 2：利用用户登录（Alice）**

我们使用 curl 命令发送 SQL 注入载荷：

```bash
curl -X POST http://localhost:8000/api/login/user \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "email=alice@example.com' AND ('1')#" \
  --data-urlencode "password=anything"
```

**预期响应：**
```json
{
  "success": true,
  "username": "alice",
  "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

我们成功获取了 Alice 的 JWT 令牌！

**步骤 3：利用管理员登录**

现在尝试管理员登录：

```bash
curl -X POST http://localhost:8000/api/login/admin \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "username=admin' || ('1')#" \
  --data-urlencode "password=anything"
```

**预期响应：**
```json
{
  "success": true,
  "username": "admin",
  "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

成功获取管理员 JWT！

**步骤 4：获取 Flags**

最后，我们检查 CTF 进度：

```bash
curl http://localhost:8000/api/flags
```

**预期响应：**
```json
{
  "ctf_enabled": true,
  "flags": {
    "total_flags": 2,
    "user_pwned": true,
    "admin_pwned": true,
    "flags_obtained": 2
  }
}
```

两个旗帜都已成功获取！

**演示总结：**

通过这个演示，我们展示了：
- SQL 注入如何绕过身份验证
- 部分清理机制的局限性
- 依赖层漏洞的实际影响

现在，让我把时间交回给 Zhenghan，他将总结关键要点。

---

## 第11页：Conclusion - Zhenghan PEI

**讲稿：**

谢谢 Dongshan 的精彩演示。现在让我总结一下这个项目的关键要点。

**项目价值：**

这个项目作为一个**教学工具**，成功展示了：

1. **依赖层安全的重要性** - 即使应用代码看起来安全，依赖库的缺陷仍然可能导致漏洞
2. **部分清理的危险性** - 基于黑名单的清理机制往往可以被绕过
3. **纵深防御的必要性** - 前端限制不能提供真正的安全保护

**教育意义：**

通过这个 CTF 挑战，学习者可以：
- 理解 SQL 注入的工作原理
- 学习如何绕过部分清理机制
- 认识到依赖审计的重要性
- 掌握真实世界的攻击技术

---

## 第11页：Key Takeaways - Zhenghan PEI

**讲稿：**

让我提炼三个关键要点：

**1. Dependency Risk（依赖风险）**

应用逻辑可以完美无缺，但如果驱动或 ORM 有缺陷（或配置错误），应用仍然脆弱。

这提醒我们：
- 安全审计必须包括依赖库审查
- 定期更新依赖库以修复已知漏洞
- 理解依赖库的行为，而不仅仅是 API

**2. Partial Sanitization is Dangerous（部分清理是危险的）**

- 依赖正则黑名单（阻止 'OR'、'SELECT'）通常可以被绕过
- 攻击者可以通过组合允许的字符来构造有效载荷
- **解决方案：** 应普遍使用参数化查询（预编译语句）

参数化查询是防止 SQL 注入的最可靠方法，因为它将数据和代码完全分离。

**3. Defense in Depth（纵深防御）**

前端限制不提供真正的安全。

- 前端验证可以被绕过
- 攻击者可以直接调用 API
- 安全必须在后端实现

**重要声明：**

*"This project is a teaching artifact, not a production reference."*

这个项目是专门为教学设计的，故意包含漏洞。它不应该用作生产系统的安全参考。

---

## 结尾页：Thank you - Zhenghan PEI

**讲稿：**

感谢大家的聆听！

我们团队很高兴能为大家展示这个 Personal Blog CTF 项目。

通过这个项目，我们希望：
- 提高对依赖层安全的认识
- 展示 SQL 注入的实际影响
- 强调纵深防御的重要性

现在，我们开放提问时间。如果大家有任何问题，无论是关于：
- 技术实现细节
- 攻击技术
- 安全最佳实践
- 或者任何其他相关问题

我们都很乐意回答。

谢谢！

---

## 过渡语句

### Zhenghan → Haihang
"现在让我们深入了解系统的技术架构。Haihang 将为大家展示系统是如何构建的，以及漏洞是如何在依赖层注入的。"

### Haihang → Peipei
"了解了架构后，让我们看看第一个挑战。Peipei 将详细介绍用户挑战，展示如何通过信息收集和 SQL 注入来获取用户旗帜。"

### Peipei → Dongshan
"完成用户挑战后，我们来看更复杂的管理员挑战。Dongshan 将展示如何发现隐藏的管理员面板，以及如何绕过更严格的清理规则。"

### Dongshan → Zhenghan
"演示完成后，让我们总结一下关键要点。Zhenghan 将提炼这个项目的核心安全教训。"

---

## 时间控制提醒

- **封面：** 30秒 - 简短介绍
- **Table of Contents：** 1分钟 - 快速概述
- **Project Overview：** 2-3分钟 - 详细但不过长
- **Architecture：** 3-4分钟 - 技术细节
- **Hidden Vulnerability：** 2-3分钟 - 核心概念
- **Challenge Scope：** 1分钟 - 快速介绍
- **User Recon：** 2分钟 - 信息收集
- **User Exploit：** 2-3分钟 - 详细解释
- **Admin Recon：** 2分钟 - 快速介绍
- **Admin Exploit：** 2-3分钟 - 详细解释
- **Demo：** 4-5分钟 - 实际操作
- **Conclusion：** 1-2分钟 - 总结
- **Key Takeaways：** 1-2分钟 - 要点提炼
- **Thank you：** 30秒 - 简短致谢

**总时长：** 23-30 分钟（不含问答）
