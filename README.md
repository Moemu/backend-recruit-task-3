# backend-recruit-task-03

*呱呱学术管家的 Python 实现*

![Black CodeStyle](https://img.shields.io/badge/Code%20Style-Black-121110.svg)
![wakatime](https://wakatime.com/badge/user/637d5886-8b47-4b82-9264-3b3b9d6add67/project/eed23219-e0a5-47c4-a854-5f852b211047.svg)
![coverage](./src/coverage.svg)

[🏨Level 1](https://github.com/Moemu/backend-recruit-task) | [🐍Level 2](https://github.com/Moemu/backend-recruit-task-2) | 📕Level 3

## 项目简介

本项目是"呱呱学术管家"的后端系统实现，使用 Python 开发。该系统旨在提供学术服务管理功能，包括用户管理、学术资源查询、任务调度等功能，采用现代化的微服务架构设计。

## 功能特性

- **用户认证与授权**：JWT 认证系统，基于角色的访问控制
- **学术资源管理**：添加、查询、更新学术资源
- **服务处理流程**：完整的服务生命周期管理
- **API 接口**：RESTful API 设计，提供前后端分离的数据交互
- **日志系统**：详细记录系统操作和错误信息
- **数据库存储**: MySQL + SQLAlchemy ORM 实现数据库存储, Redis 缓存实现

## 技术栈

- **后端框架**： FastAPI
- **数据库**： MySQL
- **ORM**： SQLAlchemy
- **身份验证**： JWT
- **文档**： APIfox
- **代码规范**： Black, mypy 类型检查
- **版本控制**： Git
- **CI/CD**： Pre-commit hooks

## 数据库设计

系统使用 MySQL 作为主数据库，通过 SQLAlchemy ORM 进行数据访问。以下是核心数据模型说明：

### 用户模型 (User)

用于存储系统用户信息，包括学生、教师和管理员。

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | BigInteger | 主键ID | 主键、自增 |
| username | String(50) | 用户名 | 唯一、非空 |
| password | String(100) | 密码(加密存储) | 非空 |
| role | Enum | 角色(student/teacher/admin) | 非空 |
| status | Boolean | 状态(true=正常/false=禁用) | 默认true |
| major_id | BigInteger | 专业ID | 可空 |
| grade | Integer | 年级 | 可空 |
| account_number | String(12) | 账号格式 | 唯一、非空 |
| create_time | DateTime | 创建时间 | 非空、自动 |
| update_time | DateTime | 更新时间 | 非空、自动更新 |

### 课程模型 (Course)

存储课程信息及其关联数据。

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | BigInteger | 主键ID | 主键、自增 |
| course_no | String(20) | 课程编号 | 唯一、非空 |
| course_name | String(50) | 课程名称 | 非空 |
| teacher_id | BigInteger | 教师ID | 非空，关联User |
| major_id | BigInteger | 专业ID | 非空 |
| grade | Integer | 年级 | 非空 |
| course_type | Integer | 课程类型(0=必修/1=选修) | 非空 |
| credit | Numeric | 学分 | 非空 |
| is_public | Boolean | 是否公开 | 默认true |
| status | Integer | 课程状态(1=已提交/2=审核通过/3=审核不通过/4=公开/0=隐藏) | 默认1 |
| course_date | JSON | 课程时间 | 非空 |
| create_time | DateTime | 创建时间 | 非空、自动 |
| update_time | DateTime | 更新时间 | 非空、自动更新 |

## 快速开始

### 环境要求

- Python 3.11+
- 虚拟环境管理工具 (如 uv, conda)

### 安装步骤

1. 克隆仓库
   ```bash
   git clone https://github.com/Moemu/backend-recruit-task-3
   cd backend-recruit-task-3
   ```

2. 创建虚拟环境（以 Conda 为例）
   ```bash
   conda create --name backend python==3.11 -y
   conda activate backend
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 启动应用
   ```bash
   python -m app.main
   ```

## 配置说明

系统通过项目根目录下的 `config.yml` 文件进行配置，支持以下配置项：

### 基础配置

- **log_level**: 日志等级，可选值 `DEBUG`、`INFO`、`WARNING`、`ERROR`，默认 `DEBUG`

### FastAPI 配置

- **title**: API 服务标题，默认 `ManagementSystem`
- **version**: API 服务版本，默认 `0.1.0`
- **host**: API 服务监听地址，默认 `127.0.0.1`
- **port**: API 服务端口，默认 `8080`

### JWT 认证配置

- **secret_key**: 32 位 hex 密钥，用于 JWT 签名，默认提供测试密钥
- **algorithm**: JWT 签名算法，默认 `HS256`
- **expire_minutes**: 令牌过期时间（分钟），默认 `60`

### 数据库配置

- **db_url**: MySQL 数据库连接字符串，默认 `mysql+aiomysql://user:pwd@localhost/college`

### Redis 配置

- **redis_host**: Redis 服务器地址，默认 `127.0.0.1`
- **redis_port**: Redis 服务端口，默认 `6379`

配置示例:

```yaml
# 日志配置
log_level: INFO

# FastAPI 配置
title: 呱呱学术管家
version: 1.0.0
host: 127.0.0.0
port: 8080

# JWT 配置
secret_key: 82ec285b5f0670c852c2e16d9776c5d17bd89a5f1dc09cdab5374a8a9ec7aa11
algorithm: HS256
expire_minutes: 120

# 数据库配置
db_url: mysql+aiomysql://username:password@db_host:3306/academic_db

# Redis 配置
redis_host: 127.0.0.1
redis_port: 6379
```

## API 文档

[APIfox 在线文档](https://apifox.com/apidoc/shared-b29cd1cb-b0aa-4f9b-af29-23a55ca6bba3)

FastAPI 文档: `http://localhost:8080/docs` (其中 `localhost:8080` 为 API 服务器)

## 单元测试

一般测试:

```
pytest
```

代码覆盖率测试:

```
coverage run -m pytest
```

## 目录结构

```
D:\PROJECT\BACKEND-RECRUIT-TASK-3
│  .gitignore                  # Git 忽略规则
│  .pre-commit-config.yaml     # pre-commit 钩子配置
│  config.yml                  # 项目配置文件（可选，全局配置）
│  LICENSE                     # 项目许可证
│  README.md                   # 项目说明文档
│
├─app                          # 主应用目录
│  │  main.py                  # FastAPI 入口文件，初始化并挂载路由
│  │
│  ├─api                       # 路由层，定义 API 端点
│  │  │  auth.py              # 登录/注册/登出等认证路由
│  │  │  student.py           # 学生相关接口路由
│  │  └─ teacher.py           # 教师相关接口路由
│  │
│  ├─core                      # 核心配置与工具
│  │  │  config.py            # 读取与管理环境配置
│  │  │  logger.py            # 日志配置
│  │  │  redis.py             # Redis 初始化与封装
│  │  │  sql.py               # SQLAlchemy 数据库连接配置
│  │
│  ├─deps                      # 依赖注入函数模块
│  │      auth.py             # 认证相关依赖（如当前用户提取）
│  │      sql.py              # 数据库会话依赖
│  │
│  ├─models                    # ORM 模型定义
│  │  │  course.py            # 课程模型
│  │  │  department.py        # 院系模型
│  │  │  major.py             # 专业模型
│  │  │  user.py              # 用户模型
│  │  │  __init__.py          # 模型子包初始化
│  │
│  ├─repositories              # 数据访问层（仓库模式）
│  │  │  course.py            # 课程数据操作封装
│  │  │  user.py              # 用户数据操作封装
│  │  │  __init__.py          # 仓库子包初始化
│  │
│  ├─schemas                   # Pydantic 数据校验模型
│  │      auth.py             # 登录/注册请求与响应模型
│  │      course.py           # 课程相关请求与响应模型
│  │      __init__.py         # Schemas 子包初始化
│  │
│  ├─services                  # 业务逻辑服务层
│  │  │  auth_service.py      # 认证服务逻辑封装
│  │  │  token_blacklist.py   # Token 黑名单服务（登出逻辑）
│
└─logs                         # 日志输出目录
        2025-05-22.log         # 示例日志文件（按日期命名）

```