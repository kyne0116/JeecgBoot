# 软著申报AI系统 - 任务分解文档

> **版本**: v1.0
> **日期**: 2025-12-01
> **基于**: 软著申报AI系统-详细设计文档 v1.0

---

## 任务状态说明

- 🔴 **未开始**: 任务尚未启动
- 🟡 **进行中**: 任务正在开发
- 🟢 **已完成**: 任务开发完成并通过测试
- 🔵 **测试中**: 任务开发完成，等待测试
- ⚫ **已阻塞**: 任务因依赖或其他问题被阻塞

---

## 第一阶段：基础设施和环境准备（1-2天）

### T001: 项目初始化和环境配置

**状态**: 🔴 未开始
**优先级**: P0 - 最高
**预估工作量**: 0.5天
**依赖任务**: 无
**负责人**: 待分配

**任务描述**:
- [ ] 创建JeecgBoot模块 `jeecg-module-copyright`
- [ ] 配置Spring AI Alibaba依赖（1.1.0.0-M5）
- [ ] 配置Dashscope API Key
- [ ] 配置异步任务线程池
- [ ] 配置WebSocket支持
- [ ] 配置文件上传下载路径

**测试要点**:
- [ ] 项目能正常启动
- [ ] Spring AI Alibaba配置生效
- [ ] 线程池配置正确
- [ ] WebSocket配置正常

**产出物**:
- `pom.xml` 依赖配置
- `application.yml` 基础配置
- `application-prod.yml` 生产环境配置

---

### T002: 数据库设计和初始化

**状态**: 🔴 未开始
**优先级**: P0 - 最高
**预估工作量**: 1天
**依赖任务**: T001
**负责人**: 待分配

**任务描述**:
- [ ] 创建数据库表结构（5张表）
  - [ ] `us_session` - 会话表
  - [ ] `us_message` - 对话记录表
  - [ ] `us_file` - 生成文件表
  - [ ] `us_agent_log` - Agent执行日志表
  - [ ] `us_config` - 系统配置表
- [ ] 创建索引优化查询性能
- [ ] 插入初始系统配置数据
- [ ] 生成MyBatis-Plus实体类

**数据库表设计详细说明**:

#### 5.1 会话表 (us_session)
```sql
CREATE TABLE us_session (
    id VARCHAR(64) PRIMARY KEY COMMENT '会话ID(格式:用户名_时间戳_哈希前8位)',
    user_id VARCHAR(32) NOT NULL COMMENT '用户ID',
    username VARCHAR(50) COMMENT '用户名',
    software_name VARCHAR(255) COMMENT '软件名称',
    short_name VARCHAR(100) COMMENT '软件简称',
    version VARCHAR(50) COMMENT '软件版本号',
    status VARCHAR(20) NOT NULL DEFAULT 'CLARIFYING' COMMENT '状态:CLARIFYING/GENERATING/CHECKING/COMPLETED/FAILED',
    requirement_json TEXT COMMENT '需求JSON(CopyrightRequirement)',
    progress_json TEXT COMMENT '进度JSON(包含各Agent执行状态)',
    error_message TEXT COMMENT '错误信息',
    retry_count INT DEFAULT 0 COMMENT '重试次数',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    create_by VARCHAR(50) COMMENT '创建人',
    update_by VARCHAR(50) COMMENT '更新人',

    INDEX idx_user_id (user_id),
    INDEX idx_username (username),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time),
    INDEX idx_software_name (software_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='软著申报会话表';
```

#### 5.2 对话记录表 (us_message)
```sql
CREATE TABLE us_message (
    id VARCHAR(32) PRIMARY KEY COMMENT '消息ID',
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    sequence_no INT NOT NULL COMMENT '消息序号(同一会话内递增)',
    role VARCHAR(20) NOT NULL COMMENT '角色:user/assistant/system',
    content TEXT NOT NULL COMMENT '消息内容',
    message_type VARCHAR(20) DEFAULT 'text' COMMENT '消息类型:text/file/status/error',
    agent_name VARCHAR(100) COMMENT 'Agent名称(如果是Agent发送的消息)',
    metadata_json TEXT COMMENT '消息元数据JSON',
    token_count INT COMMENT '消息Token数量',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_session_id (session_id),
    INDEX idx_sequence_no (session_id, sequence_no),
    INDEX idx_create_time (create_time),
    INDEX idx_role (role),
    FOREIGN KEY (session_id) REFERENCES us_session(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='软著申报对话记录表';
```

#### 5.3 生成文件表 (us_file)
```sql
CREATE TABLE us_file (
    id VARCHAR(32) PRIMARY KEY COMMENT '文件ID',
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    file_type VARCHAR(20) NOT NULL COMMENT '文件类型:source_code/info_form/desc_doc',
    file_category VARCHAR(50) COMMENT '文件分类:申报材料/质检报告/其他',
    filename VARCHAR(255) NOT NULL COMMENT '文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径(相对路径)',
    file_size BIGINT COMMENT '文件大小(字节)',
    mime_type VARCHAR(100) COMMENT 'MIME类型',
    file_extension VARCHAR(10) COMMENT '文件扩展名',
    quality_status VARCHAR(20) DEFAULT 'checking' COMMENT '质量状态:checking/passed/failed',
    quality_score INT COMMENT '质量得分(0-100)',
    quality_report_json TEXT COMMENT '质检报告JSON',
    code_lines INT COMMENT '代码行数(仅代码文件)',
    doc_word_count INT COMMENT '文档字数(仅文档文件)',
    version INT DEFAULT 1 COMMENT '文件版本号',
    is_latest TINYINT(1) DEFAULT 1 COMMENT '是否最新版本',
    generated_by VARCHAR(100) COMMENT '生成者Agent名称',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_session_id (session_id),
    INDEX idx_file_type (file_type),
    INDEX idx_quality_status (quality_status),
    INDEX idx_version (session_id, file_type, version),
    INDEX idx_latest (session_id, is_latest),
    UNIQUE KEY uk_session_type_version (session_id, file_type, version),
    FOREIGN KEY (session_id) REFERENCES us_session(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='软著申报生成文件表';
```

#### 5.4 Agent执行日志表 (us_agent_log)
```sql
CREATE TABLE us_agent_log (
    id VARCHAR(32) PRIMARY KEY COMMENT '日志ID',
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    agent_name VARCHAR(100) NOT NULL COMMENT 'Agent名称',
    agent_type VARCHAR(50) COMMENT 'Agent类型:ReactAgent/NormalAgent',
    execution_phase VARCHAR(50) COMMENT '执行阶段:clarify/generate/check',
    status VARCHAR(20) NOT NULL COMMENT '执行状态:STARTED/RUNNING/COMPLETED/FAILED',
    start_time DATETIME COMMENT '开始时间',
    end_time DATETIME COMMENT '结束时间',
    duration_ms BIGINT COMMENT '执行时长(毫秒)',
    input_params JSON COMMENT '输入参数JSON',
    output_result JSON COMMENT '输出结果JSON',
    error_message TEXT COMMENT '错误信息',
    error_stack TEXT COMMENT '错误堆栈',
    retry_count INT DEFAULT 0 COMMENT '重试次数',
    model_name VARCHAR(50) COMMENT '使用的模型名称',
    total_tokens INT COMMENT '总Token消耗',
    prompt_tokens INT COMMENT 'Prompt Token数',
    completion_tokens INT COMMENT '完成Token数',
    cost_amount DECIMAL(10,4) COMMENT '费用金额',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_session_id (session_id),
    INDEX idx_agent_name (agent_name),
    INDEX idx_status (status),
    INDEX idx_start_time (start_time),
    INDEX idx_execution_phase (execution_phase),
    INDEX idx_duration (duration_ms),
    FOREIGN KEY (session_id) REFERENCES us_session(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent执行日志表';
```

#### 5.5 系统配置表 (us_config)
```sql
CREATE TABLE us_config (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '配置ID',
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    config_value TEXT NOT NULL COMMENT '配置值',
    config_type VARCHAR(20) DEFAULT 'string' COMMENT '配置类型:string/int/bool/json/decimal',
    config_group VARCHAR(50) DEFAULT 'system' COMMENT '配置分组:system/agent/file/mcp',
    description VARCHAR(500) COMMENT '配置描述',
    is_system TINYINT(1) DEFAULT 0 COMMENT '是否系统配置(系统配置不可删除)',
    is_encrypted TINYINT(1) DEFAULT 0 COMMENT '是否加密存储',
    sort_order INT DEFAULT 0 COMMENT '排序顺序',
    status TINYINT(1) DEFAULT 1 COMMENT '状态:0-禁用,1-启用',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    create_by VARCHAR(50) COMMENT '创建人',
    update_by VARCHAR(50) COMMENT '更新人',

    INDEX idx_config_group (config_group),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- 初始化系统配置数据
INSERT INTO us_config (config_key, config_value, config_type, config_group, description, is_system, sort_order) VALUES
-- Agent配置
('agent.clarify.max_iterations', '10', 'int', 'agent', '需求澄清Agent最大对话轮次', 1, 1),
('agent.clarify.timeout', '300000', 'int', 'agent', '需求澄清Agent超时时间(毫秒)', 1, 2),
('agent.quality.max_retries', '2', 'int', 'agent', '质量检查最大重试次数', 1, 3),
('agent.quality.timeout', '600000', 'int', 'agent', '质量检查超时时间(毫秒)', 1, 4),
('agent.codegen.timeout', '900000', 'int', 'agent', '代码生成超时时间(毫秒)', 1, 5),

-- 文件配置
('file.storage.base_path', '/data/copyright-files', 'string', 'file', '文件存储基础路径', 1, 10),
('file.storage.max_size', '104857600', 'int', 'file', '单文件最大大小(字节,100MB)', 1, 11),
('file.allowed.extensions', '.java,.py,.js,.docx,.zip', 'string', 'file', '允许的文件扩展名', 1, 12),
('file.temp.cleanup_days', '7', 'int', 'file', '临时文件清理天数', 1, 13),

-- 代码生成配置
('code.target_lines.min', '5000', 'int', 'agent', '目标代码最小行数', 1, 20),
('code.target_lines.max', '6000', 'int', 'agent', '目标代码最大行数', 1, 21),
('code.quality.min_score', '70', 'int', 'agent', '代码质量最低得分', 1, 22),

-- 文档配置
('doc.word_count.min', '3000', 'int', 'agent', '文档最小字数', 1, 30),
('doc.word_count.max', '5000', 'int', 'agent', '文档最大字数', 1, 31),
('doc.font.name', '仿宋', 'string', 'agent', '文档字体名称', 1, 32),
('doc.font.size', '12', 'int', 'agent', '文档字体大小', 1, 33),

-- MCP配置
('mcp.word_server.url', 'http://localhost:8765', 'string', 'mcp', 'MCP Word服务器地址', 1, 40),
('mcp.word_server.timeout', '30000', 'int', 'mcp', 'MCP请求超时时间(毫秒)', 1, 41),
('mcp.word_server.health_check_interval', '60000', 'int', 'mcp', 'MCP健康检查间隔(毫秒)', 1, 42),

-- AI模型配置
('ai.model.default', 'qwen-max', 'string', 'system', '默认AI模型', 1, 50),
('ai.model.temperature', '0.7', 'decimal', 'system', '模型温度参数', 1, 51),
('ai.model.max_tokens', '4000', 'int', 'system', '最大Token数', 1, 52),

-- 系统配置
('system.concurrent.max_sessions', '10', 'int', 'system', '最大并发会话数', 1, 60),
('system.session.expire_hours', '24', 'int', 'system', '会话过期时间(小时)', 1, 61),
('system.log.retention_days', '30', 'int', 'system', '日志保留天数', 1, 62);
```

#### 5.6 性能优化索引
```sql
-- 会话列表查询优化(用户查看自己的会话列表)
CREATE INDEX idx_session_user_status_time ON us_session(user_id, status, create_time DESC);

-- 消息历史查询优化(按时间顺序加载消息)
CREATE INDEX idx_message_session_time ON us_message(session_id, create_time ASC);

-- 文件查询优化(查询会话的最新文件)
CREATE INDEX idx_file_session_type_quality ON us_file(session_id, file_type, quality_status);
CREATE INDEX idx_file_latest ON us_file(session_id, is_latest, file_type);

-- Agent日志分析优化(性能监控和问题排查)
CREATE INDEX idx_agent_log_name_time ON us_agent_log(agent_name, start_time DESC);
CREATE INDEX idx_agent_log_session_phase ON us_agent_log(session_id, execution_phase, status);

-- 配置查询优化
CREATE INDEX idx_config_group_status ON us_config(config_group, status);
```

**测试要点**:
- [ ] 所有表创建成功
- [ ] 索引创建正确
- [ ] 外键约束生效
- [ ] 实体类生成正确，字段映射准确
- [ ] 初始配置数据插入成功

**产出物**:
- `init-db.sql` 数据库初始化脚本
- 实体类（表名映射）：
  - `CopyrightSession.java` → 表 `us_session`
  - `CopyrightMessage.java` → 表 `us_message`
  - `CopyrightFile.java` → 表 `us_file`
  - `CopyrightAgentLog.java` → 表 `us_agent_log`
  - `CopyrightConfig.java` → 表 `us_config`

---

### T003: MCP Word服务器环境准备

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 0.5天
**依赖任务**: T001
**负责人**: 待分配

**任务描述**:
- [ ] 部署Office-Word-MCP-Server
- [ ] 配置MCP服务器访问地址
- [ ] 实现MCP客户端工具类 `McpClientUtil`
- [ ] 实现MCP健康检查 `McpHealthChecker`
- [ ] 测试Markdown转Word功能
- [ ] 测试字体设置功能

**测试要点**:
- [ ] MCP服务器能正常启动
- [ ] 健康检查接口返回正常
- [ ] Markdown转Word转换成功
- [ ] 字体设置功能正常

**产出物**:
- `McpClientUtil.java` - MCP客户端工具类
- `McpHealthChecker.java` - 健康检查组件
- `McpConfig.java` - MCP配置类

---

## 第二阶段：后端核心功能开发（3-4天）

### T004: 会话管理核心功能

**状态**: 🔴 未开始
**优先级**: P0 - 最高
**预估工作量**: 1天
**依赖任务**: T002
**负责人**: 待分配

**任务描述**:
- [ ] 实现会话ID生成器 `SessionIdGenerator`
- [ ] 实现会话Service层 `CopyrightSessionService`
  - [ ] 创建会话
  - [ ] 更新会话状态
  - [ ] 查询用户会话列表
  - [ ] 获取会话详情
- [ ] 实现会话Controller `CopyrightSessionController`
  - [ ] POST `/copyright/session/create` - 创建会话
  - [ ] GET `/copyright/session/list` - 查询会话列表
  - [ ] GET `/copyright/session/detail/{sessionId}` - 获取会话详情
  - [ ] PUT `/copyright/session/{sessionId}/status` - 更新状态

**测试要点**:
- [ ] 会话ID生成规则正确（用户名_时间戳_MD5前8位）
- [ ] 会话创建成功并返回会话ID
- [ ] 会话列表查询正确，支持分页
- [ ] 会话详情返回完整信息
- [ ] 状态更新成功

**产出物**:
- `SessionIdGenerator.java`
- `CopyrightSessionService.java`
- `CopyrightSessionController.java`
- 单元测试用例

---

### T005: 对话消息管理功能

**状态**: 🔴 未开始
**优先级**: P0 - 最高
**预估工作量**: 0.5天
**依赖任务**: T004
**负责人**: 待分配

**任务描述**:
- [ ] 实现消息Service层 `CopyrightMessageService`
  - [ ] 保存对话消息
  - [ ] 查询会话消息历史
  - [ ] 构建对话上下文
- [ ] 实现消息Controller `CopyrightMessageController`
  - [ ] POST `/copyright/message/save` - 保存消息
  - [ ] GET `/copyright/message/history/{sessionId}` - 获取消息历史

**测试要点**:
- [ ] 消息保存成功，包含用户消息和AI响应
- [ ] 消息历史按时间顺序返回
- [ ] 支持分页加载历史消息
- [ ] 对话上下文构建正确

**产出物**:
- `CopyrightMessageService.java`
- `CopyrightMessageController.java`
- 单元测试用例

---

### T006: WebSocket实时通信

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 1天
**依赖任务**: T005
**负责人**: 待分配

**任务描述**:
- [ ] 实现WebSocket配置 `WebSocketConfig`
- [ ] 实现WebSocket处理器 `CopyrightChatWebSocket`
  - [ ] 连接建立和断开处理
  - [ ] 消息接收和发送
  - [ ] 会话绑定管理
- [ ] 实现WebSocket消息模型 `WebSocketMessage`
- [ ] 实现会话-连接映射管理

**测试要点**:
- [ ] WebSocket连接成功建立
- [ ] 消息能正常收发
- [ ] 断线重连机制正常
- [ ] 多用户隔离正确
- [ ] 会话状态实时推送

**产出物**:
- `WebSocketConfig.java`
- `CopyrightChatWebSocket.java`
- `WebSocketMessage.java`
- WebSocket测试脚本

---

### T007: 文件管理功能

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 1天
**依赖任务**: T004
**负责人**: 待分配

**任务描述**:
- [ ] 实现文件Service层 `CopyrightFileService`
  - [ ] 保存文件记录
  - [ ] 更新文件质量状态
  - [ ] 查询会话文件列表
  - [ ] 获取最新版本文件
- [ ] 实现文件下载服务 `FileDownloadService`
  - [ ] 单文件下载
  - [ ] 批量打包下载（ZIP）
  - [ ] 流式下载优化
- [ ] 实现文件Controller `CopyrightFileController`
  - [ ] GET `/copyright/file/list/{sessionId}` - 文件列表
  - [ ] GET `/copyright/file/download/{fileId}` - 单文件下载
  - [ ] GET `/copyright/file/download-all/{sessionId}` - 批量下载

**测试要点**:
- [ ] 文件记录保存正确
- [ ] 文件列表查询正确
- [ ] 单文件下载成功
- [ ] ZIP打包下载成功，文件完整
- [ ] 大文件下载不会导致内存溢出

**产出物**:
- `CopyrightFileService.java`
- `FileDownloadService.java`
- `CopyrightFileController.java`
- 文件下载测试用例

---

## 第三阶段：Agent开发（5-7天）

### T008: Agent基础架构

**状态**: 🔴 未开始
**优先级**: P0 - 最高
**预估工作量**: 1天
**依赖任务**: T002
**负责人**: 待分配

**任务描述**:
- [ ] 定义Agent基础接口 `CopyrightAgent`
- [ ] 定义Agent上下文 `AgentContext`
- [ ] 定义Agent执行结果 `AgentResult`
- [ ] 实现Agent事件发布器 `AgentEventPublisher`
- [ ] 实现Agent事件监听器 `AgentEventListener`
- [ ] 实现Agent日志记录AOP `BusinessLogAspect`

**测试要点**:
- [ ] Agent接口定义清晰
- [ ] 上下文传递正确
- [ ] 事件发布和监听正常
- [ ] 日志记录准确

**产出物**:
- `CopyrightAgent.java` - Agent接口
- `AgentContext.java` - Agent上下文
- `AgentResult.java` - Agent结果
- `AgentEventPublisher.java` - 事件发布器
- `AgentEventListener.java` - 事件监听器
- `BusinessLogAspect.java` - 日志AOP

---

### T009: Agent 1 - ReactClarifyAgent（需求澄清）

**状态**: 🔴 未开始
**优先级**: P0 - 最高
**预估工作量**: 2天
**依赖任务**: T008
**负责人**: 待分配

**任务描述**:
- [ ] 实现ReactClarifyAgent核心逻辑
- [ ] 配置ReactAgent指令和参数
- [ ] 实现需求完整性检查工具 `requirementCheckTool`
- [ ] 实现结构化数据提取工具 `extractDataTool`
- [ ] 定义需求对象 `CopyrightRequirement`
- [ ] 实现多轮对话上下文管理
- [ ] 实现需求澄清完成判断

**测试要点**:
- [ ] 能正确引导用户提供必填信息
- [ ] 多轮对话上下文保持正确
- [ ] 需求完整性检查准确
- [ ] 能从对话中提取结构化数据
- [ ] 9个必填字段全部收集后判断完成
- [ ] 最多10轮对话限制生效

**产出物**:
- `ReactClarifyAgent.java`
- `CopyrightRequirement.java`
- `CopyrightAgentToolsConfig.java`
- 单元测试和集成测试用例

---

### T010: Agent 2 - ReactCodeGenAgent（代码生成）

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 2天
**依赖任务**: T008
**负责人**: 待分配

**任务描述**:
- [ ] 实现ReactCodeGenAgent核心逻辑
- [ ] 实现代码生成计划制定 `generateCodePlan`
- [ ] 实现按模块生成代码 `generateModuleCode`
- [ ] 实现代码质量检查器 `CodeQualityChecker`
- [ ] 实现代码行数统计功能
- [ ] 实现代码行数调整逻辑（5000-6000行）
- [ ] 实现源代码打包功能（ZIP）

**测试要点**:
- [ ] 生成代码结构完整（实体、DAO、Service、Controller等）
- [ ] 代码有效行数在5000-6000之间
- [ ] 代码符合Java规范
- [ ] 代码能正常编译
- [ ] ZIP打包成功，结构清晰

**产出物**:
- `ReactCodeGenAgent.java`
- `CodeQualityChecker.java`
- `CodeGenerationPlan.java`
- 代码生成测试用例

---

### T011: Agent 3 - ReactFormFillAgent（表格填报）

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 1.5天
**依赖任务**: T008
**负责人**: 待分配

**任务描述**:
- [ ] 准备Word模板文件 `软著信息采集表模板.docx`
- [ ] 实现ReactFormFillAgent核心逻辑
- [ ] 实现POI工具类 `PoiWordUtil`
  - [ ] 填充静态占位符
  - [ ] 填充动态表格（功能列表）
  - [ ] 保存Word文档
- [ ] 实现数据映射 `prepareFillData`
- [ ] 实现表格验证 `validateForm`

**测试要点**:
- [ ] Word模板加载成功
- [ ] 所有占位符正确替换
- [ ] 动态表格行数正确
- [ ] 功能列表填充完整
- [ ] 创新点填充正确
- [ ] 生成的Word文档格式正确

**产出物**:
- `ReactFormFillAgent.java`
- `PoiWordUtil.java`
- `软著信息采集表模板.docx`
- 表格填报测试用例

---

### T012: Agent 4 - ReactDocWriterAgent（文档撰写）

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 1.5天
**依赖任务**: T008, T003
**负责人**: 待分配

**任务描述**:
- [ ] 实现ReactDocWriterAgent核心逻辑
- [ ] 实现Markdown文档内容生成 `generateMarkdownDoc`
- [ ] 集成MCP客户端调用
  - [ ] Markdown转Word
  - [ ] 设置仿宋字体12号
- [ ] 实现文档格式验证 `validateDocument`
- [ ] 实现字数统计（3000-5000字）

**测试要点**:
- [ ] Markdown文档生成符合申报要求
- [ ] 章节结构完整（概述、功能、架构、创新点等）
- [ ] 成功转换为Word文档
- [ ] 字体为仿宋12号
- [ ] 字数在3000-5000之间
- [ ] 文档内容专业严谨

**产出物**:
- `ReactDocWriterAgent.java`
- 文档生成测试用例

---

### T013: Agent 5 - ReactQualityCheckAgent（质量检查）

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 2天
**依赖任务**: T008
**负责人**: 待分配

**任务描述**:
- [ ] 实现ReactQualityCheckAgent核心逻辑
- [ ] 配置ReactAgent质检指令
- [ ] 实现代码质量检查工具 `codeQualityTool`
  - [ ] 代码行数统计
  - [ ] 代码结构检查
  - [ ] 代码质量分析
- [ ] 实现表格验证工具 `formValidationTool`
  - [ ] 必填字段检查
  - [ ] 格式验证
- [ ] 实现文档检查工具 `documentCheckTool`
  - [ ] 字体格式检查
  - [ ] 章节结构检查
  - [ ] 字数统计
  - [ ] 内容质量检查
- [ ] 生成质检报告 `QualityCheckReport`

**测试要点**:
- [ ] 代码行数统计准确
- [ ] 代码结构检查正确
- [ ] 表格必填项校验准确
- [ ] 文档字体检查正确
- [ ] 文档字数统计准确
- [ ] 质检报告详细明确
- [ ] 不合格项能准确识别

**产出物**:
- `ReactQualityCheckAgent.java`
- `QualityCheckToolsConfig.java`
- `QualityCheckReport.java`
- 质量检查测试用例

---

### T014: Agent编排器和协作机制

**状态**: 🔴 未开始
**优先级**: P0 - 最高
**预估工作量**: 2天
**依赖任务**: T009, T010, T011, T012, T013
**负责人**: 待分配

**任务描述**:
- [ ] 实现Agent编排器 `CopyrightAgentOrchestrator`
- [ ] 实现编排流程控制
  - [ ] Phase 1: 需求澄清等待
  - [ ] Phase 2: 并行生成（代码、表格、文档）
  - [ ] Phase 3: 质量检查循环（最多2次重试）
  - [ ] Phase 4: 完成状态更新
- [ ] 实现重新生成失败组件逻辑
- [ ] 实现异步任务管理
- [ ] 实现进度跟踪和状态推送

**测试要点**:
- [ ] 需求未完成时正确等待
- [ ] 三个Agent能并行执行
- [ ] 质量检查循环逻辑正确
- [ ] 失败组件能正确重新生成
- [ ] 最多重试2次限制生效
- [ ] 状态实时推送到前端
- [ ] 完整流程端到端测试通过

**产出物**:
- `CopyrightAgentOrchestrator.java`
- `OrchestratorResult.java`
- 编排器集成测试用例

---

## 第四阶段：申报记录管理（2天）

### T015: 申报记录查询功能

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 1天
**依赖任务**: T004
**负责人**: 待分配

**任务描述**:
- [ ] 实现申报记录Controller `CopyrightRecordController`
- [ ] 实现分页查询接口
  - [ ] 支持软件名称模糊查询
  - [ ] 支持状态筛选
  - [ ] 支持时间范围筛选
  - [ ] 按创建时间倒序
- [ ] 实现会话详情查询
  - [ ] 会话基本信息
  - [ ] 消息记录
  - [ ] 生成文件列表
- [ ] 实现权限验证（只能查看自己的记录）

**测试要点**:
- [ ] 分页查询正确
- [ ] 筛选条件生效
- [ ] 只返回当前用户的记录
- [ ] 详情信息完整
- [ ] 权限验证生效

**产出物**:
- `CopyrightRecordController.java`
- `CopyrightSessionQuery.java`
- `CopyrightSessionDetailVO.java`
- 查询接口测试用例

---

### T016: 申报产物下载功能

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 0.5天
**依赖任务**: T007, T015
**负责人**: 待分配

**任务描述**:
- [ ] 实现批量下载接口（已在T007实现）
- [ ] 优化ZIP压缩性能
- [ ] 添加下载权限验证
- [ ] 实现下载日志记录

**测试要点**:
- [ ] 批量下载成功
- [ ] ZIP文件完整性
- [ ] 权限验证生效
- [ ] 下载日志记录准确

**产出物**:
- 下载功能测试用例

---

## 第五阶段：前端开发（4-5天）

### T017: 前端项目初始化

**状态**: 🔴 未开始
**优先级**: P0 - 最高
**预估工作量**: 0.5天
**依赖任务**: T001
**负责人**: 待分配

**任务描述**:
- [ ] 创建Vue组件目录结构
- [ ] 配置路由 `router.js`
- [ ] 配置Pinia状态管理 `copyrightStore.js`
- [ ] 配置API接口模块 `copyrightApi.js`
- [ ] 配置WebSocket管理 `useWebSocket.js`

**测试要点**:
- [ ] 路由配置正确
- [ ] 状态管理初始化正常
- [ ] API模块能正常调用

**产出物**:
- 前端项目结构
- 路由配置文件
- Pinia Store
- API模块

---

### T018: 用户对话页面 - 会话列表组件

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 1天
**依赖任务**: T017
**负责人**: 待分配

**任务描述**:
- [ ] 实现会话列表组件 `SessionList.vue`
- [ ] 实现会话卡片显示
  - [ ] 显示软件名称（从第一个问题提取）
  - [ ] 显示会话状态
  - [ ] 显示创建时间
- [ ] 实现会话切换功能
- [ ] 实现新建申报按钮
- [ ] 实现会话搜索功能

**测试要点**:
- [ ] 会话列表正确显示
- [ ] 会话状态显示正确
- [ ] 点击切换会话成功
- [ ] 新建申报功能正常
- [ ] 搜索功能生效

**产出物**:
- `SessionList.vue`
- 会话列表样式文件

---

### T019: 用户对话页面 - 聊天窗口组件

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 1.5天
**依赖任务**: T017, T006
**负责人**: 待分配

**任务描述**:
- [ ] 实现聊天窗口组件 `ChatWindow.vue`
- [ ] 实现消息列表组件 `MessageList.vue`
  - [ ] 用户消息显示（右侧）
  - [ ] AI消息显示（左侧）
  - [ ] 消息时间显示
  - [ ] 自动滚动到最新消息
- [ ] 实现消息输入组件 `MessageInput.vue`
  - [ ] 文本输入框
  - [ ] 发送按钮
  - [ ] 快捷键支持（Enter发送）
- [ ] 实现WebSocket消息收发
- [ ] 实现打字中状态显示

**测试要点**:
- [ ] 消息列表正确显示
- [ ] 消息能正常发送
- [ ] WebSocket实时接收AI响应
- [ ] 自动滚动到底部
- [ ] 打字中状态显示正常

**产出物**:
- `ChatWindow.vue`
- `MessageList.vue`
- `MessageInput.vue`
- 聊天窗口样式文件

---

### T020: 用户对话页面 - 文件列表组件

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 1天
**依赖任务**: T017, T007
**负责人**: 待分配

**任务描述**:
- [ ] 实现文件列表组件 `FilesList.vue`
- [ ] 实现文件卡片显示
  - [ ] 文件图标（根据类型）
  - [ ] 文件名称
  - [ ] 文件大小
  - [ ] 下载按钮
- [ ] 实现单文件下载功能
- [ ] 实现批量下载功能
- [ ] 实现文件生成进度显示

**测试要点**:
- [ ] 文件列表正确显示
- [ ] 文件图标正确
- [ ] 单文件下载成功
- [ ] 批量下载成功
- [ ] 生成进度实时更新

**产出物**:
- `FilesList.vue`
- 文件列表样式文件

---

### T021: 用户对话页面 - 整体布局

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 1天
**依赖任务**: T018, T019, T020
**负责人**: 待分配

**任务描述**:
- [ ] 实现主容器组件 `CopyrightChatApp.vue`
- [ ] 实现三栏布局（会话列表、聊天窗口、文件列表）
- [ ] 实现顶部用户信息栏 `UserHeader.vue`
  - [ ] 用户名显示
  - [ ] 新建申报按钮
  - [ ] 申报记录按钮
  - [ ] 退出按钮
- [ ] 实现响应式布局
- [ ] 实现组件间状态同步

**测试要点**:
- [ ] 整体布局美观
- [ ] 响应式布局适配不同屏幕
- [ ] 组件间状态同步正确
- [ ] 用户信息显示正确
- [ ] 按钮功能正常

**产出物**:
- `CopyrightChatApp.vue`
- `UserHeader.vue`
- 整体样式文件

---

### T022: 申报记录列表页面

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 1.5天
**依赖任务**: T017, T015
**负责人**: 待分配

**任务描述**:
- [ ] 实现申报记录列表页面 `CopyrightRecordList.vue`
- [ ] 实现筛选条件组件
  - [ ] 软件名称输入框
  - [ ] 申报状态下拉框
  - [ ] 时间范围选择器
  - [ ] 搜索按钮
- [ ] 实现数据表格
  - [ ] 序号、软件名称、申请人、状态、创建时间
  - [ ] 操作列（查看、下载、删除）
- [ ] 实现分页组件
- [ ] 实现查看详情弹窗
- [ ] 实现删除确认对话框

**测试要点**:
- [ ] 列表数据正确显示
- [ ] 筛选条件生效
- [ ] 分页功能正常
- [ ] 查看详情弹窗显示完整信息
- [ ] 下载功能正常
- [ ] 删除功能正常

**产出物**:
- `CopyrightRecordList.vue`
- 记录列表样式文件

---

## 第六阶段：系统监控和日志（1-2天）

### T023: 系统监控功能

**状态**: 🔴 未开始
**优先级**: P2 - 中
**预估工作量**: 1天
**依赖任务**: T014
**负责人**: 待分配

**任务描述**:
- [ ] 实现系统监控组件 `SystemMonitor`
- [ ] 配置Micrometer指标
  - [ ] 会话创建计数器
  - [ ] Agent执行时间
  - [ ] 文件下载计数器
- [ ] 集成Prometheus
- [ ] 配置Grafana监控面板

**测试要点**:
- [ ] 指标正确记录
- [ ] Prometheus能采集数据
- [ ] Grafana面板显示正常

**产出物**:
- `SystemMonitor.java`
- Prometheus配置
- Grafana面板配置

---

### T024: 业务日志和审计

**状态**: 🔴 未开始
**优先级**: P2 - 中
**预估工作量**: 0.5天
**依赖任务**: T008
**负责人**: 待分配

**任务描述**:
- [ ] 完善Agent执行日志AOP
- [ ] 实现关键操作审计日志
  - [ ] 会话创建
  - [ ] 文件生成
  - [ ] 文件下载
- [ ] 配置日志文件滚动策略
- [ ] 配置ELK集成（可选）

**测试要点**:
- [ ] Agent执行日志完整
- [ ] 审计日志记录关键操作
- [ ] 日志格式规范
- [ ] 日志文件正常滚动

**产出物**:
- 日志配置文件
- 审计日志组件

---

## 第七阶段：集成测试和优化（2-3天）

### T025: 端到端集成测试

**状态**: 🔴 未开始
**优先级**: P0 - 最高
**预估工作量**: 2天
**依赖任务**: T014, T021, T022
**负责人**: 待分配

**任务描述**:
- [ ] 编写端到端测试场景
  - [ ] 场景1：完整的软著申报流程
  - [ ] 场景2：多用户并发申报
  - [ ] 场景3：质量检查失败重试
  - [ ] 场景4：中断后恢复
- [ ] 性能测试
  - [ ] 并发用户测试
  - [ ] Agent执行性能测试
  - [ ] 文件下载性能测试
- [ ] 压力测试
  - [ ] 数据库连接池压力测试
  - [ ] WebSocket连接数测试

**测试要点**:
- [ ] 所有场景测试通过
- [ ] 系统稳定性良好
- [ ] 性能指标达标
- [ ] 无内存泄漏

**产出物**:
- 端到端测试用例
- 性能测试报告
- 压力测试报告

---

### T026: Bug修复和优化

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 1天
**依赖任务**: T025
**负责人**: 待分配

**任务描述**:
- [ ] 修复集成测试发现的Bug
- [ ] 优化性能瓶颈
- [ ] 优化用户体验
- [ ] 代码重构和优化
- [ ] 代码审查

**测试要点**:
- [ ] 所有已知Bug已修复
- [ ] 性能达到预期
- [ ] 代码质量良好

**产出物**:
- Bug修复记录
- 优化报告

---

## 第八阶段：部署和上线（1-2天）

### T027: Docker部署配置

**状态**: 🔴 未开始
**优先级**: P1 - 高
**预估工作量**: 1天
**依赖任务**: T026
**负责人**: 待分配

**任务描述**:
- [ ] 编写Dockerfile
- [ ] 编写docker-compose.yml
- [ ] 配置MySQL容器
- [ ] 配置Redis容器
- [ ] 配置MCP Word服务器容器
- [ ] 配置数据卷挂载
- [ ] 配置网络

**测试要点**:
- [ ] Docker镜像构建成功
- [ ] 容器能正常启动
- [ ] 服务间通信正常
- [ ] 数据持久化正常

**产出物**:
- `Dockerfile`
- `docker-compose.yml`
- 部署文档

---

### T028: 生产环境部署

**状态**: 🔴 未开始
**优先级**: P0 - 最高
**预估工作量**: 0.5天
**依赖任务**: T027
**负责人**: 待分配

**任务描述**:
- [ ] 准备生产环境配置文件
- [ ] 配置环境变量
- [ ] 初始化生产数据库
- [ ] 部署应用到生产环境
- [ ] 配置反向代理（Nginx）
- [ ] 配置SSL证书
- [ ] 配置域名解析

**测试要点**:
- [ ] 生产环境正常运行
- [ ] HTTPS访问正常
- [ ] 所有功能正常工作
- [ ] 监控告警正常

**产出物**:
- 生产环境配置
- 部署文档
- 运维手册

---

### T029: 用户文档和培训

**状态**: 🔴 未开始
**优先级**: P2 - 中
**预估工作量**: 1天
**依赖任务**: T028
**负责人**: 待分配

**任务描述**:
- [ ] 编写用户操作手册
- [ ] 编写管理员手册
- [ ] 录制操作演示视频
- [ ] 准备培训材料
- [ ] 组织用户培训

**测试要点**:
- [ ] 文档完整清晰
- [ ] 视频演示清楚
- [ ] 用户能够独立操作

**产出物**:
- 用户操作手册
- 管理员手册
- 演示视频
- 培训材料

---

## 任务统计

| 阶段 | 任务数 | 预估工作量 | 优先级分布 |
|------|--------|-----------|----------|
| 第一阶段：基础设施 | 3 | 2天 | P0:2, P1:1 |
| 第二阶段：后端核心 | 4 | 4天 | P0:2, P1:2 |
| 第三阶段：Agent开发 | 7 | 12天 | P0:3, P1:4 |
| 第四阶段：记录管理 | 2 | 1.5天 | P1:2 |
| 第五阶段：前端开发 | 6 | 6.5天 | P0:1, P1:5 |
| 第六阶段：监控日志 | 2 | 1.5天 | P2:2 |
| 第七阶段：集成测试 | 2 | 3天 | P0:1, P1:1 |
| 第八阶段：部署上线 | 3 | 2.5天 | P0:1, P1:1, P2:1 |
| **总计** | **29** | **33天** | **P0:10, P1:16, P2:3** |

---

## 建议开发计划

### Week 1 (第1周)
- 完成基础设施和环境准备（T001-T003）
- 完成后端核心功能开发（T004-T007）
- 开始Agent基础架构和需求澄清Agent（T008-T009）

### Week 2 (第2周)
- 完成其他4个Agent开发（T010-T013）
- 完成Agent编排器（T014）
- 完成申报记录管理（T015-T016）

### Week 3 (第3周)
- 完成前端所有组件开发（T017-T022）
- 完成系统监控和日志（T023-T024）

### Week 4 (第4周)
- 完成集成测试和优化（T025-T026）
- 完成部署和上线（T027-T029）
- 系统试运行

---

## 任务跟踪表格

| 任务编号 | 任务名称 | 负责人 | 状态 | 开始日期 | 完成日期 | 备注 |
|---------|---------|--------|------|---------|---------|------|
| T001 | 项目初始化和环境配置 | - | 🔴 | - | - | - |
| T002 | 数据库设计和初始化 | - | 🔴 | - | - | - |
| T003 | MCP Word服务器环境准备 | - | 🔴 | - | - | - |
| T004 | 会话管理核心功能 | - | 🔴 | - | - | - |
| T005 | 对话消息管理功能 | - | 🔴 | - | - | - |
| T006 | WebSocket实时通信 | - | 🔴 | - | - | - |
| T007 | 文件管理功能 | - | 🔴 | - | - | - |
| T008 | Agent基础架构 | - | 🔴 | - | - | - |
| T009 | ReactClarifyAgent | - | 🔴 | - | - | - |
| T010 | ReactCodeGenAgent | - | 🔴 | - | - | - |
| T011 | ReactFormFillAgent | - | 🔴 | - | - | - |
| T012 | ReactDocWriterAgent | - | 🔴 | - | - | - |
| T013 | ReactQualityCheckAgent | - | 🔴 | - | - | - |
| T014 | Agent编排器和协作机制 | - | 🔴 | - | - | - |
| T015 | 申报记录查询功能 | - | 🔴 | - | - | - |
| T016 | 申报产物下载功能 | - | 🔴 | - | - | - |
| T017 | 前端项目初始化 | - | 🔴 | - | - | - |
| T018 | 会话列表组件 | - | 🔴 | - | - | - |
| T019 | 聊天窗口组件 | - | 🔴 | - | - | - |
| T020 | 文件列表组件 | - | 🔴 | - | - | - |
| T021 | 用户对话页面整体布局 | - | 🔴 | - | - | - |
| T022 | 申报记录列表页面 | - | 🔴 | - | - | - |
| T023 | 系统监控功能 | - | 🔴 | - | - | - |
| T024 | 业务日志和审计 | - | 🔴 | - | - | - |
| T025 | 端到端集成测试 | - | 🔴 | - | - | - |
| T026 | Bug修复和优化 | - | 🔴 | - | - | - |
| T027 | Docker部署配置 | - | 🔴 | - | - | - |
| T028 | 生产环境部署 | - | 🔴 | - | - | - |
| T029 | 用户文档和培训 | - | 🔴 | - | - | - |

---

## 风险和注意事项

### 技术风险
1. **Spring AI Alibaba稳定性**: 使用的是1.1.0.0-M5版本（Milestone版本），可能存在Bug
   - **缓解措施**: 提前测试关键功能，准备回退方案

2. **MCP集成复杂度**: Office-Word-MCP-Server可能存在兼容性问题
   - **缓解措施**: T003阶段充分测试，准备备选方案（纯POI实现）

3. **代码生成质量**: LLM生成的代码可能不符合要求
   - **缓解措施**: 严格的质量检查机制，多次重试

### 开发风险
1. **任务依赖复杂**: 部分任务存在强依赖关系
   - **缓解措施**: 严格按照任务顺序开发，关键路径优先

2. **工作量估算偏差**: 实际开发时间可能超出预估
   - **缓解措施**: 留有20%缓冲时间，定期review进度

### 资源风险
1. **人力资源不足**: 如果只有1-2名开发人员，时间会延长
   - **缓解措施**: 合理分配任务，前后端可并行开发

---

## 下一步行动

1. **立即开始**: T001 项目初始化和环境配置
2. **分配任务**: 根据团队成员技能分配任务负责人
3. **建立沟通机制**: 每日站会，周度review
4. **搭建CI/CD**: 自动化测试和部署流水线
5. **风险监控**: 定期评估风险和进度

---

**祝开发顺利！🚀**
