# 软件著作权申报AI系统 - 技术方案

> **版本**: v1.0
> **日期**: 2025-12-01
> **技术栈**: Spring Boot 3.5.5 + Spring AI Alibaba 1.1.0.0-M5 + JeecgBoot 3.8.3

---

## 一、系统概述

### 1.1 项目目标

基于JeecgBoot和Spring AI Alibaba构建B/S架构的软件著作权申报AI应用程序，通过多Agent协作，将用户的简单描述转换为完整的软著申报材料。

### 1.2 核心功能

1. **智能对话**：通过ReactAgent与用户多轮对话，澄清申报需求
2. **材料生成**：自动生成三类申报材料
   - 源代码（5000-6000行有效代码）
   - 软著信息采集表.docx
   - 申报说明文档.docx（仿宋字体）
3. **质量检查**：自动检查生成材料的完整性和规范性
4. **本地存储**：材料按用户和会话组织存储

---

## 二、系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                   前端层 (Vue3 + AntDV)                  │
│          聊天界面 │ 文件预览 │ 材料下载                  │
└────────────────────────┬────────────────────────────────┘
                         ↓ WebSocket / HTTP
┌─────────────────────────────────────────────────────────┐
│                  后端服务层 (Spring Boot)                │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Agent编排层 (Spring AI Alibaba)           │  │
│  │                                                   │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │ Agent 1: ReactClarifyAgent (需求澄清)       │ │  │
│  │  │   - 最大对话轮次: 10轮                       │ │  │
│  │  │   - 输出: CopyrightRequirement (JSON)       │ │  │
│  │  └──────────────────┬──────────────────────────┘ │  │
│  │                     ↓                             │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │    AgentOrchestrator (编排器)               │ │  │
│  │  │    并行调度3个生成Agent                      │ │  │
│  │  └─┬──────────┬──────────┬─────────────────────┘ │  │
│  │    ↓          ↓          ↓                        │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │  │
│  │  │ Agent 2:     │ │ Agent 3:     │ │ Agent 4:     │ │  │
│  │  │ReactCodeGen  │ │ReactFormFill │ │ReactDocWriter│ │  │
│  │  │(代码生成)    │ │(表格填报)    │ │(文档撰写)    │ │  │
│  │  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ │  │
│  │    └────────┴───────────┘                        │  │
│  │              ↓                                    │  │
│  │  ┌──────────────────────────────────────────────┐ │  │
│  │  │ Agent 5: ReactQualityCheckAgent (质量检查)   │ │  │
│  │  │   - 检查代码行数                             │ │  │
│  │  │   - 验证表格完整性                           │ │  │
│  │  │   - 检查文档格式                             │ │  │
│  │  └──────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              外部服务 & 资源层                           │
│   通义千问API │ 本地文件系统 │ Office-Word-MCP          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Agent协作流程

```
用户输入
   ↓
┌──────────────────────────────────┐
│ ReactClarifyAgent (需求澄清)      │
│ - 多轮对话（最多10轮）             │
│ - Function Calling工具调用        │
│ - 需求完整性检查                  │
│ - 输出结构化JSON                  │
└─────────────┬────────────────────┘
              ↓
┌──────────────────────────────────┐
│ AgentOrchestrator (编排器)        │
│ - 接收CopyrightRequirement        │
│ - 并行启动3个生成Agent            │
└─┬────────┬────────┬───────────────┘
  ↓        ↓        ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Agent 2    │ │   Agent 3    │ │   Agent 4    │
│ReactCodeGen  │ │ReactFormFill │ │ReactDocWriter│
│  (代码生成)  │ │  (表格填报)  │ │  (文档撰写)  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       └────────┴───────────┘
                ↓
┌──────────────────────────────────┐
│ ReactQualityCheckAgent (质量检查) │
│ - 验证代码行数: 5000-6000行       │
│ - 检查表格字段完整性              │
│ - 验证文档格式: 仿宋、结构完整    │
│ - 输出检查报告                    │
└─────────────┬────────────────────┘
              ↓
    ┌──────────────────┐
    │ 质量检查不通过？   │
    └─┬────────────┬───┘
    YES            NO
      ↓             ↓
   重新生成      返回用户
   (自动修正)    (3个文件)
```

---

## 三、5个Agent设计

### Agent命名规范

| 序号 | 英文名称 | 中文名称 | 类型 |
|------|---------|---------|------|
| Agent 1 | ReactClarifyAgent | 需求澄清Agent | ReactAgent |
| Agent 2 | ReactCodeGenAgent | 代码生成Agent | 普通Agent |
| Agent 3 | ReactFormFillAgent | 表格填报Agent | 普通Agent |
| Agent 4 | ReactDocWriterAgent | 文档撰写Agent | 普通Agent |
| Agent 5 | ReactQualityCheckAgent | 质量检查Agent | ReactAgent |

> **命名说明**: 所有Agent统一使用`React`前缀，保持命名一致性。Agent 2/3/4虽然不是ReactAgent实现，但为了统一规范也使用React前缀。

---

### 3.1 Agent 1: ReactClarifyAgent（需求澄清Agent）

**类型**: ReactAgent（推理-行动Agent）

**职责**: 通过多轮对话引导用户提供完整的软著申报信息

**配置**:
- **最大对话轮次**: 10轮
- **工具函数**:
  - `checkRequirementCompleteness()`: 检查需求完整度
  - `extractStructuredData()`: 提取结构化JSON
- **输出**: `CopyrightRequirement` (JSON对象)

**必须收集的信息**:
1. 软件全称和简称
2. 软件版本号
3. 软件分类
4. 主要编程语言
5. 技术架构（前端/后端框架）
6. 核心功能列表（至少3个）
7. 技术创新点（至少2个）
8. 申请人信息（企业/个人）
9. 开发完成日期

**实现方式**: Spring AI Alibaba ReactAgent + Function Calling

---

### 3.2 Agent 2: ReactCodeGenAgent（代码生成Agent）

**类型**: 普通Agent（基于ChatClient）

**职责**: 根据需求生成5000-6000行有效代码

**生成策略**:
1. 根据技术栈分模块生成（实体类、DAO、Service、Controller、工具类、配置类）
2. 每个模块分配代码行数
3. 过滤注释和空行，统计有效代码行数
4. 行数不足时补充代码

**输出**: 多个源代码文件（.java/.py等）

**实现方式**: ChatClient + Prompt Engineering

---

### 3.3 Agent 3: ReactFormFillAgent（表格填报Agent）

**类型**: 普通Agent

**职责**: 填写《软著信息采集表.docx》

**处理流程**:
1. 加载Word模板（包含占位符）
2. 使用Apache POI解析文档结构
3. 根据字段映射填充数据
4. 处理动态表格（如功能列表）
5. 保存为.docx文件

**输出**: 软著信息采集表_[时间戳].docx

**实现方式**: Apache POI

---

### 3.4 Agent 4: ReactDocWriterAgent（文档撰写Agent）

**类型**: 普通Agent

**职责**: 生成软著申报说明文档

**处理流程**:
1. LLM生成Markdown内容（包含：软件概述、功能说明、技术架构、创新点）
2. 调用Office-Word-MCP将Markdown转换为Word文档
3. 设置仿宋字体、12号字

**输出**: 软著申报说明_[时间戳].docx

**实现方式**: ChatClient + Office-Word-MCP（HTTP SSE）

---

### 3.5 Agent 5: ReactQualityCheckAgent（质量检查Agent）⭐新增

**类型**: ReactAgent（推理-判断Agent）

**职责**: 检查生成材料的质量，确保符合软著申报规范

**检查项**:

| 检查项 | 标准 | 不通过处理 |
|--------|------|-----------|
| 代码行数 | 5000-6000行有效代码 | 提示ReactCodeGenAgent重新生成 |
| 代码结构 | 包含完整的分层结构 | 提示补充缺失模块 |
| 表格完整性 | 必填字段全部填写 | 提示ReactFormFillAgent重新填报 |
| 文档格式 | 仿宋字体、章节完整 | 提示ReactDocWriterAgent重新生成 |
| 文档内容 | 功能描述详细、创新点明确 | 提示优化内容 |

**工具函数**:
- `checkCodeQuality()`: 验证代码质量
- `checkDocFormCompleteness()`: 验证表格完整性
- `checkDocWriterFormat()`: 验证文档格式

**输出**:
- 质量检查通过 → 返回用户
- 质量检查不通过 → 触发对应Agent重新生成（最多重试2次）

**实现方式**: ReactAgent + Function Calling

---

## 四、技术实现要点

### 4.1 核心依赖

```xml
<!-- Spring AI Alibaba -->
<dependency>
    <groupId>com.alibaba.cloud.ai</groupId>
    <artifactId>spring-ai-alibaba-starter-dashscope</artifactId>
    <version>1.1.0.0-M5</version>
</dependency>
<dependency>
    <groupId>com.alibaba.cloud.ai</groupId>
    <artifactId>spring-ai-alibaba-agent-framework</artifactId>
    <version>1.1.0.0-M5</version>
</dependency>

<!-- Apache POI (Word处理) -->
<dependency>
    <groupId>org.apache.poi</groupId>
    <artifactId>poi-ooxml</artifactId>
    <version>5.2.3</version>
</dependency>
```

### 4.2 配置文件

```yaml
spring:
  ai:
    dashscope:
      api-key: ${DASHSCOPE_API_KEY}
      chat:
        options:
          model: qwen-max
          temperature: 0.7

# MCP配置
mcp:
  word-server:
    url: http://localhost:8765
    timeout: 30000

# 文件存储
copyright:
  storage:
    base-path: D:/copyright-files
```

### 4.3 模块结构

```
jeecg-boot-module/
└── jeecg-boot-module-copyright/
    ├── pom.xml
    └── src/main/java/org/jeecg/modules/copyright/
        ├── config/
        │   ├── CopyrightAgentConfig.java      # Agent配置
        │   └── McpConfig.java                 # MCP客户端配置
        ├── controller/
        │   └── CopyrightChatController.java   # REST API
        ├── websocket/
        │   └── CopyrightChatWebSocket.java    # WebSocket
        ├── service/
        │   ├── agent/
        │   │   ├── ReactClarifyAgent.java         # Agent 1: 需求澄清
        │   │   ├── ReactCodeGenAgent.java         # Agent 2: 代码生成
        │   │   ├── ReactFormFillAgent.java        # Agent 3: 表格填报
        │   │   ├── ReactDocWriterAgent.java       # Agent 4: 文档撰写
        │   │   └── ReactQualityCheckAgent.java    # Agent 5: 质量检查
        │   ├── CopyrightAgentOrchestrator.java  # 编排器
        │   └── CopyrightChatService.java      # 业务服务
        ├── entity/
        │   ├── CopyrightSession.java
        │   ├── CopyrightMessage.java
        │   └── CopyrightFile.java
        ├── vo/
        │   ├── CopyrightRequirement.java      # 需求对象
        │   └── QualityCheckReport.java        # 质检报告
        └── util/
            ├── PoiWordUtil.java               # POI工具
            └── McpClientUtil.java             # MCP客户端
```

---

## 五、数据库设计

### 5.1 会话表

```sql
CREATE TABLE copyright_session (
    id VARCHAR(32) PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL,
    status VARCHAR(20) NOT NULL,  -- clarifying/generating/checking/completed
    requirement_json TEXT,
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL,
    INDEX idx_user_id (user_id)
);
```

### 5.2 对话记录表

```sql
CREATE TABLE copyright_message (
    id VARCHAR(32) PRIMARY KEY,
    session_id VARCHAR(32) NOT NULL,
    role VARCHAR(20) NOT NULL,    -- user/assistant
    content TEXT NOT NULL,
    create_time DATETIME NOT NULL,
    INDEX idx_session_id (session_id)
);
```

### 5.3 生成文件表

```sql
CREATE TABLE copyright_file (
    id VARCHAR(32) PRIMARY KEY,
    session_id VARCHAR(32) NOT NULL,
    file_type VARCHAR(20) NOT NULL,  -- code/doc_form/doc_desc
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    quality_status VARCHAR(20),      -- passed/failed/checking
    create_time DATETIME NOT NULL,
    INDEX idx_session_id (session_id)
);
```

---

## 六、前端设计

### 6.1 技术栈

- Vue 3 Composition API
- Ant Design Vue 4.x
- WebSocket（实时聊天）
- Markdown-it（消息渲染）

### 6.2 主要页面

**聊天界面**:
- 左侧：消息列表 + 输入框
- 右侧：生成的文件列表（带下载/预览按钮）
- 底部：质量检查报告（如有）

---

## 七、Office-Word-MCP集成

### 7.1 部署方式

```bash
# 启动MCP Server（HTTP SSE模式）
cd D:\02_Dev\Workspace\GitHub\Office-Word-MCP-Server
python word_mcp_server.py --transport sse --port 8765
```

### 7.2 Java客户端调用

```java
@Component
public class McpClientUtil {
    private static final String MCP_SERVER_URL = "http://localhost:8765";

    // 创建文档
    public String createDocument(String filename, String title);

    // 添加段落（仿宋）
    public void addParagraph(String filename, String content);

    // Markdown转Word
    public String generateFromMarkdown(String markdown, String outputPath);
}
```

---

## 八、实施步骤

### Phase 1: 基础模块搭建（2天）
- 创建`jeecg-boot-module-copyright`模块
- 配置Spring AI Alibaba依赖
- 设计并创建数据库表

### Phase 2: Agent实现（5天）
- 实现ReactClarifyAgent（2天）
- 实现ReactCodeGenAgent、ReactFormFillAgent、ReactDocWriterAgent（2天）
- 实现ReactQualityCheckAgent（1天）

### Phase 3: 编排器开发（2天）
- 实现AgentOrchestrator
- 集成5个Agent
- 实现并行执行和质量检查循环

### Phase 4: MCP集成（2天）
- 启动Office-Word-MCP-Server
- 封装Java HTTP客户端
- 测试文档生成功能

### Phase 5: 前端开发（3天）
- 实现Vue聊天界面
- WebSocket实时通信
- 文件下载和预览功能

### Phase 6: 联调测试（2天）
- 端到端流程测试
- 质量检查测试
- 性能优化

---

## 九、关键技术要点

### 9.1 Agent协作模式

采用**混合模式**：
- ReactClarifyAgent（顺序执行）
- → ReactCodeGenAgent、ReactFormFillAgent、ReactDocWriterAgent（并行执行）
- → ReactQualityCheckAgent（顺序执行）
- → 不通过则重新生成（最多2次）

### 9.2 ReactAgent优势

- ✅ 自动推理：无需手动编写对话状态机
- ✅ 工具调用：自动选择合适的工具函数
- ✅ 多轮对话：内置对话历史管理（最多10轮）
- ✅ 可观测性：enableLogging()查看推理过程

### 9.3 质量保证机制

1. **需求阶段**：ReactClarifyAgent通过工具函数验证完整性
2. **生成阶段**：各Agent按规范生成材料
3. **检查阶段**：ReactQualityCheckAgent统一质检
4. **重试机制**：不通过自动重新生成（最多2次）

---

## 十、参考资料

- [Spring AI Alibaba 官方文档](https://java2ai.com/docs/overview/)
- [Spring AI Alibaba GitHub](https://github.com/alibaba/spring-ai-alibaba)
- [Office-Word-MCP-Server](https://github.com/kyne0116/Office-Word-MCP-Server)
- [JeecgBoot 官方文档](http://www.jeecg.com/)

---

## 附录：CopyrightRequirement数据结构

```json
{
  "softwareName": "软件全称",
  "shortName": "软件简称",
  "version": "v1.0",
  "category": "应用软件",
  "codeLanguage": "Java",
  "techStack": "Spring Boot + Vue3",
  "features": [
    {"name": "功能1", "description": "详细描述"},
    {"name": "功能2", "description": "详细描述"}
  ],
  "innovations": ["创新点1", "创新点2"],
  "architecture": "前后端分离架构",
  "applicant": {
    "name": "企业/个人名称",
    "type": "enterprise/individual"
  },
  "devCompleteDate": "2025-12-01"
}
```

---

**文档结束**
