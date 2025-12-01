# 软著申报AI系统 - 详细设计文档

> **版本**: v1.0
> **日期**: 2025-12-01
> **基于**: JeecgBoot 3.8.3 + Spring AI Alibaba 1.1.0.0-M5

---

## 一、系统整体架构

### 1.1 系统概述

软著申报AI系统采用**多用户、多会话、多Agent协作**的架构设计，支持企业用户同时申报多个软件著作权。系统通过智能对话收集需求，自动生成申报材料，并提供完整的申报记录管理。

### 1.2 系统特性

- ✅ **多租户支持**: 支持多个用户独立使用
- ✅ **会话隔离**: 每个软著申报独立会话，数据隔离
- ✅ **智能对话**: 5个Agent协作，自动生成申报材料
- ✅ **记录管理**: 完整的申报记录查询和下载功能
- ✅ **实时通信**: WebSocket实时对话体验

---

## 二、用户对话页面设计

### 2.1 页面架构

```
┌─────────────────────────────────────────────────────────┐
│                    软著申报AI系统                        │
├─────────────────────────────────────────────────────────┤
│ 用户信息: 张三 | 新建申报 | 申报记录 | 退出               │
├─────────────────────────────────────────────────────────┤
│ 左侧: 会话列表                │ 右侧: 聊天界面              │
│ ┌─────────────────────────┐   │ ┌─────────────────────────┐ │
│ │ ○ 进销存管理系统 v1.0    │   │ │ 💬 AI助手               │ │
│ │   状态: 生成中...       │   │ │ 您好！我是软著申报...     │ │
│ │   创建: 2025-12-01     │   │ │                         │ │
│ │                        │   │ │ 👤 用户                 │ │
│ │ ○ CRM客户管理系统       │   │ │ 我想申报一个...         │ │
│ │   状态: 已完成         │   │ │                         │ │
│ │   创建: 2025-11-28     │   │ │ 💬 AI助手               │ │
│ │                        │   │ │ 请详细描述...           │ │
│ └─────────────────────────┘   │ └─────────────────────────┘ │
│                              │ ┌─────────────────────────┐ │
│                              │ │ [输入框] 发送           │ │
│                              │ └─────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ 底部: 生成文件列表                                       │
│ 📁 源代码.zip | 📄 信息采集表.docx | 📄 申报说明.docx     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 会话管理机制

#### 2.2.1 会话ID生成规则

```java
/**
 * 会话ID生成规则：用户账号+年月日时分秒+第一个问题MD5哈希
 * 例：user001_20251201143025_a1b2c3d4e5f6...
 */
public class SessionIdGenerator {
    public static String generateSessionId(String username, String firstQuestion) {
        // 1. 获取当前时间戳 (yyyyMMddHHmmss)
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));

        // 2. 拼接字符串：用户名 + 时间戳 + 第一个问题
        String rawString = username + timestamp + firstQuestion;

        // 3. MD5哈希
        String hash = DigestUtils.md5Hex(rawString);

        // 4. 格式化：username_timestamp_hash(前8位)
        return String.format("%s_%s_%s", username, timestamp, hash.substring(0, 8));
    }
}
```

#### 2.2.2 会话状态管理

```java
public enum SessionStatus {
    CLARIFYING("需求澄清中"),      // Agent1工作中
    GENERATING("材料生成中"),      // Agent2/3/4并行工作中
    CHECKING("质量检查中"),        // Agent5工作中
    COMPLETED("已完成"),           // 所有Agent完成
    FAILED("生成失败");            // 质检不通过且重试次数用尽

    private final String description;
}
```

### 2.3 前端组件设计

#### 2.3.1 主要Vue组件

```javascript
// 1. 主容器组件
CopyrightChatApp.vue
├── components/
│   ├── SessionList.vue          // 左侧会话列表
│   ├── ChatWindow.vue           // 右侧聊天窗口
│   │   ├── MessageList.vue      // 消息列表
│   │   └── MessageInput.vue     // 输入框
│   ├── FilesList.vue           // 底部文件列表
│   └── UserHeader.vue          // 顶部用户信息

// 2. WebSocket管理
useWebSocket.js                 // Composition API
├── connect()                   // 建立连接
├── sendMessage()              // 发送消息
├── onMessage()                // 接收消息
└── disconnect()               // 断开连接
```

#### 2.3.2 状态管理

```javascript
// stores/copyrightStore.js (Pinia)
export const useCopyrightStore = defineStore('copyright', {
  state: () => ({
    sessions: [],           // 会话列表
    currentSession: null,   // 当前会话
    messages: [],          // 当前会话消息
    files: [],             // 生成的文件列表
    wsStatus: 'disconnected' // WebSocket状态
  }),

  actions: {
    // 创建新会话
    async createSession(firstQuestion) {
      const sessionId = await api.createSession(firstQuestion);
      // 添加到会话列表
      this.sessions.unshift({
        id: sessionId,
        status: 'CLARIFYING',
        createTime: new Date(),
        firstQuestion: firstQuestion.substring(0, 20) + '...'
      });
      this.currentSession = sessionId;
    },

    // 切换会话
    switchSession(sessionId) {
      this.currentSession = sessionId;
      this.loadMessages(sessionId);
      this.loadFiles(sessionId);
    }
  }
});
```

---

## 三、申报记录列表页面设计

### 3.1 列表页面架构

```
┌─────────────────────────────────────────────────────────┐
│                   软著申报记录管理                        │
├─────────────────────────────────────────────────────────┤
│ 筛选条件: [软件名称] [申报状态▼] [时间范围] [搜索]         │
├─────────────────────────────────────────────────────────┤
│ 序号│软件名称    │申请人│状态    │创建时间    │操作        │
│ ────┼──────────┼─────┼────────┼───────────┼──────────  │
│  1  │进销存管理  │张三  │已完成   │2025-12-01 │查看│下载│删除│
│  2  │CRM客户管理 │李四  │生成中   │2025-11-30 │查看│   │   │
│  3  │OA办公系统  │王五  │已完成   │2025-11-28 │查看│下载│删除│
├─────────────────────────────────────────────────────────┤
│                    [1][2][3]...[尾页]                   │
└─────────────────────────────────────────────────────────┘
```

### 3.2 功能设计

#### 3.2.1 列表查询API

```java
@RestController
@RequestMapping("/copyright/records")
public class CopyrightRecordController {

    /**
     * 分页查询申报记录
     */
    @GetMapping("/list")
    public Result<IPage<CopyrightSessionVO>> list(
            @RequestParam(defaultValue = "1") Integer pageNo,
            @RequestParam(defaultValue = "10") Integer pageSize,
            CopyrightSessionQuery query) {

        LambdaQueryWrapper<CopyrightSession> wrapper = new LambdaQueryWrapper<>();

        // 软件名称模糊查询
        if (StrUtil.isNotBlank(query.getSoftwareName())) {
            wrapper.like(CopyrightSession::getRequirementJson, query.getSoftwareName());
        }

        // 状态筛选
        if (StrUtil.isNotBlank(query.getStatus())) {
            wrapper.eq(CopyrightSession::getStatus, query.getStatus());
        }

        // 时间范围
        if (query.getCreateTimeStart() != null) {
            wrapper.ge(CopyrightSession::getCreateTime, query.getCreateTimeStart());
        }
        if (query.getCreateTimeEnd() != null) {
            wrapper.le(CopyrightSession::getCreateTime, query.getCreateTimeEnd());
        }

        // 当前用户的记录
        wrapper.eq(CopyrightSession::getUserId, getCurrentUserId());

        // 按创建时间倒序
        wrapper.orderByDesc(CopyrightSession::getCreateTime);

        IPage<CopyrightSession> page = new Page<>(pageNo, pageSize);
        IPage<CopyrightSession> result = copyrightSessionService.page(page, wrapper);

        return Result.OK(result);
    }
}
```

#### 3.2.2 会话详情查看

```java
/**
 * 获取会话详情（消息记录）
 */
@GetMapping("/detail/{sessionId}")
public Result<CopyrightSessionDetailVO> getDetail(@PathVariable String sessionId) {
    // 1. 验证会话权限
    CopyrightSession session = copyrightSessionService.getById(sessionId);
    if (!Objects.equals(session.getUserId(), getCurrentUserId())) {
        throw new JeecgBootException("无权限访问该会话");
    }

    // 2. 获取消息记录
    List<CopyrightMessage> messages = copyrightMessageService.list(
        new LambdaQueryWrapper<CopyrightMessage>()
            .eq(CopyrightMessage::getSessionId, sessionId)
            .orderByAsc(CopyrightMessage::getCreateTime)
    );

    // 3. 获取生成的文件
    List<CopyrightFile> files = copyrightFileService.list(
        new LambdaQueryWrapper<CopyrightFile>()
            .eq(CopyrightFile::getSessionId, sessionId)
            .eq(CopyrightFile::getQualityStatus, "passed")
    );

    return Result.OK(CopyrightSessionDetailVO.builder()
        .session(session)
        .messages(messages)
        .files(files)
        .build());
}
```

#### 3.2.3 申报产物下载

```java
/**
 * 批量下载申报产物
 */
@GetMapping("/download/{sessionId}")
public void downloadFiles(@PathVariable String sessionId, HttpServletResponse response) {
    try {
        // 1. 获取会话下的所有文件
        List<CopyrightFile> files = copyrightFileService.list(
            new LambdaQueryWrapper<CopyrightFile>()
                .eq(CopyrightFile::getSessionId, sessionId)
                .eq(CopyrightFile::getQualityStatus, "passed")
        );

        if (files.isEmpty()) {
            throw new JeecgBootException("该会话暂无可下载文件");
        }

        // 2. 创建ZIP压缩包
        String zipFileName = "软著申报材料_" + sessionId + ".zip";
        response.setContentType("application/zip");
        response.setHeader("Content-Disposition",
            "attachment; filename=" + URLEncoder.encode(zipFileName, StandardCharsets.UTF_8));

        // 3. 压缩文件并输出
        try (ZipOutputStream zos = new ZipOutputStream(response.getOutputStream())) {
            for (CopyrightFile file : files) {
                File sourceFile = new File(file.getFilePath());
                if (sourceFile.exists()) {
                    ZipEntry entry = new ZipEntry(file.getFilename());
                    zos.putNextEntry(entry);
                    Files.copy(sourceFile.toPath(), zos);
                    zos.closeEntry();
                }
            }
        }

    } catch (Exception e) {
        log.error("文件下载失败", e);
        throw new JeecgBootException("文件下载失败: " + e.getMessage());
    }
}
```

---

## 四、各个Agent功能设计

### 4.1 Agent基础架构

```java
/**
 * Agent基础接口
 */
public interface CopyrightAgent {
    /**
     * 执行Agent任务
     */
    AgentResult execute(AgentContext context);

    /**
     * 获取Agent名称
     */
    String getAgentName();

    /**
     * 获取Agent类型
     */
    AgentType getAgentType();
}

/**
 * Agent上下文
 */
@Data
public class AgentContext {
    private String sessionId;
    private String userId;
    private CopyrightRequirement requirement;  // 需求对象
    private Map<String, Object> params;        // 扩展参数
    private String workDir;                    // 工作目录
}

/**
 * Agent执行结果
 */
@Data
public class AgentResult {
    private boolean success;
    private String message;
    private Object data;               // 具体结果数据
    private List<String> generatedFiles;  // 生成的文件列表
    private Map<String, Object> metadata; // 元数据
}
```

### 4.2 Agent 1: ReactClarifyAgent（需求澄清）

```java
@Component
@Slf4j
public class ReactClarifyAgent implements CopyrightAgent {

    @Autowired
    private ChatModel chatModel;

    @Autowired
    private ToolCallback requirementCheckTool;

    @Autowired
    private ToolCallback extractDataTool;

    /**
     * 创建ReactAgent实例
     */
    private ReactAgent createReactAgent() {
        return ReactAgent.builder()
            .name("需求澄清Agent")
            .description("通过多轮对话收集软著申报的完整需求信息")
            .model(chatModel)
            .instruction("""
                你是一个专业的软件著作权申报顾问。你的任务是通过与用户的多轮对话，
                收集完整的软件著作权申报信息。

                必须收集的信息包括：
                1. 软件全称和简称
                2. 软件版本号
                3. 软件分类（应用软件/系统软件/支撑软件/嵌入式软件）
                4. 主要编程语言
                5. 技术架构描述
                6. 核心功能列表（至少3个）
                7. 技术创新点（至少2个）
                8. 申请人信息
                9. 开发完成日期

                请循序渐进地引导用户提供这些信息，每次只问1-2个相关问题。
                """)
            .enableLogging(true)
            .maxIterations(10)  // 最多10轮对话
            .tools(requirementCheckTool, extractDataTool)
            .build();
    }

    @Override
    public AgentResult execute(AgentContext context) {
        try {
            ReactAgent agent = createReactAgent();

            // 获取对话历史
            List<CopyrightMessage> messages = getSessionMessages(context.getSessionId());

            // 构建对话上下文
            List<Message> chatHistory = buildChatHistory(messages);

            // 执行ReactAgent
            String response = agent.call(chatHistory);

            // 检查是否收集完成
            CopyrightRequirement requirement = tryExtractRequirement(response);

            return AgentResult.builder()
                .success(true)
                .message(response)
                .data(requirement)
                .build();

        } catch (Exception e) {
            log.error("ReactClarifyAgent执行失败", e);
            return AgentResult.builder()
                .success(false)
                .message("需求澄清失败: " + e.getMessage())
                .build();
        }
    }

}

/**
 * Agent工具函数配置类
 */
@Configuration
@Slf4j
class CopyrightAgentToolsConfig {

    @Autowired
    private ChatModel chatModel;

    /**
     * 需求完整性检查工具
     */
    @Bean
    @Description("检查软著申报需求信息是否完整，包含所有必填字段")
    public ToolCallback requirementCheckTool() {
        return FunctionToolCallback.builder("checkRequirement",
            (RequirementCheckRequest request) -> {
                // 检查9个必填字段是否完整
                RequirementCheckResponse response = new RequirementCheckResponse();

                Map<String, Boolean> completeness = new HashMap<>();
                completeness.put("softwareName", StrUtil.isNotBlank(request.getSoftwareName()));
                completeness.put("version", StrUtil.isNotBlank(request.getVersion()));
                completeness.put("category", StrUtil.isNotBlank(request.getCategory()));
                // ... 检查其他字段

                boolean allComplete = completeness.values().stream().allMatch(Boolean::booleanValue);

                response.setComplete(allComplete);
                response.setCompleteness(completeness);
                response.setMissingFields(getMissingFields(completeness));

                return response;
            })
            .description("检查软著申报需求信息是否完整")
            .inputType(RequirementCheckRequest.class)
            .build();
    }

    /**
     * 结构化数据提取工具
     */
    @Bean
    @Description("从对话内容中提取结构化的软著申报信息")
    public ToolCallback extractDataTool() {
        return FunctionToolCallback.builder("extractRequirement",
            (ExtractDataRequest request) -> {
                // 使用LLM将自然语言描述转换为结构化JSON
                String prompt = String.format("""
                    请将以下对话内容提取为结构化的软著申报信息JSON：

                    对话内容：%s

                    请严格按照CopyrightRequirement的JSON格式返回，必须包含所有必填字段。
                    """, request.getConversationText());

                ChatResponse response = chatModel.call(
                    new Prompt(prompt,
                        ChatOptionsBuilder.builder()
                            .temperature(0.1f)  // 低温度保证准确性
                            .build())
                );

                // 解析JSON为CopyrightRequirement对象
                return JSON.parseObject(response.getResult().getOutput().getContent(),
                    CopyrightRequirement.class);
            })
            .description("从对话内容中提取结构化的软著申报信息")
            .inputType(ExtractDataRequest.class)
            .build();
    }

    private List<String> getMissingFields(Map<String, Boolean> completeness) {
        return completeness.entrySet().stream()
            .filter(entry -> !entry.getValue())
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
    }
}
```

### 4.3 Agent 2: ReactCodeGenAgent（代码生成）

```java
@Component
@Slf4j
public class ReactCodeGenAgent implements CopyrightAgent {

    @Autowired
    private ChatModel chatModel;

    @Autowired
    private CodeQualityChecker codeQualityChecker;

    @Override
    public AgentResult execute(AgentContext context) {
        try {
            CopyrightRequirement requirement = context.getRequirement();
            String workDir = context.getWorkDir();

            // 1. 生成代码生成计划
            CodeGenerationPlan plan = generateCodePlan(requirement);

            // 2. 按模块生成代码
            List<String> generatedFiles = new ArrayList<>();
            for (CodeModule module : plan.getModules()) {
                List<String> moduleFiles = generateModuleCode(module, requirement, workDir);
                generatedFiles.addAll(moduleFiles);
            }

            // 3. 检查代码行数
            CodeQualityReport report = codeQualityChecker.checkCode(generatedFiles);
            if (report.getEffectiveLines() < 5000 || report.getEffectiveLines() > 6000) {
                // 补充或优化代码
                adjustCodeLines(generatedFiles, report, workDir);
            }

            // 4. 打包代码
            String zipFile = packageSourceCode(generatedFiles, workDir);

            return AgentResult.builder()
                .success(true)
                .message("代码生成完成，共生成 " + report.getEffectiveLines() + " 行有效代码")
                .generatedFiles(List.of(zipFile))
                .metadata(Map.of("codeReport", report))
                .build();

        } catch (Exception e) {
            log.error("ReactCodeGenAgent执行失败", e);
            return AgentResult.builder()
                .success(false)
                .message("代码生成失败: " + e.getMessage())
                .build();
        }
    }

    /**
     * 生成代码生成计划
     */
    private CodeGenerationPlan generateCodePlan(CopyrightRequirement requirement) {
        String prompt = String.format("""
            根据以下软件需求，制定代码生成计划：

            软件名称：%s
            技术栈：%s
            核心功能：%s

            请设计合理的代码结构，包含：
            1. 实体类模块（约800行）
            2. DAO数据访问层（约1000行）
            3. Service业务逻辑层（约1500行）
            4. Controller控制层（约1000行）
            5. 工具类模块（约500行）
            6. 配置类模块（约200-400行）

            总计5000-6000行有效代码。
            """, requirement.getSoftwareName(), requirement.getTechStack(),
            requirement.getFeatures().stream()
                .map(f -> f.getName() + ":" + f.getDescription())
                .collect(Collectors.joining("；")));

        ChatResponse response = chatModel.call(new Prompt(prompt));
        return parseCodePlan(response.getResult().getOutput().getContent());
    }

    /**
     * 生成模块代码
     */
    private List<String> generateModuleCode(CodeModule module,
                                           CopyrightRequirement requirement,
                                           String workDir) {

        List<String> files = new ArrayList<>();

        for (CodeClass codeClass : module.getClasses()) {
            String prompt = String.format("""
                生成%s模块的%s类，要求：

                类名：%s
                功能：%s
                技术栈：%s

                请生成完整的Java代码，包含：
                - 完整的类声明和注解
                - 所有必要的字段和方法
                - 适当的业务逻辑实现
                - 必要的注释说明

                代码风格：企业级开发规范
                """, module.getName(), codeClass.getType(),
                codeClass.getClassName(), codeClass.getDescription(),
                requirement.getTechStack());

            ChatResponse response = chatModel.call(new Prompt(prompt,
                ChatOptionsBuilder.builder()
                    .temperature(0.3f)
                    .build()));

            String code = response.getResult().getOutput().getContent();
            String fileName = codeClass.getClassName() + ".java";
            String filePath = Paths.get(workDir, module.getPackagePath(), fileName).toString();

            // 保存文件
            saveCodeFile(filePath, code);
            files.add(filePath);
        }

        return files;
    }
}
```

### 4.4 Agent 3: ReactFormFillAgent（表格填报）

```java
@Component
@Slf4j
public class ReactFormFillAgent implements CopyrightAgent {

    @Autowired
    private PoiWordUtil poiWordUtil;

    private static final String FORM_TEMPLATE_PATH = "templates/软著信息采集表模板.docx";

    @Override
    public AgentResult execute(AgentContext context) {
        try {
            CopyrightRequirement requirement = context.getRequirement();
            String workDir = context.getWorkDir();

            // 1. 加载Word模板
            String templatePath = getTemplateFile(FORM_TEMPLATE_PATH);

            // 2. 准备填充数据
            Map<String, Object> fillData = prepareFillData(requirement);

            // 3. 填充表格
            String outputFileName = "软著信息采集表_" + context.getSessionId() + ".docx";
            String outputPath = Paths.get(workDir, outputFileName).toString();

            poiWordUtil.fillWordTemplate(templatePath, outputPath, fillData);

            // 4. 验证填充结果
            FormValidationResult validation = validateForm(outputPath, requirement);

            return AgentResult.builder()
                .success(validation.isValid())
                .message(validation.isValid() ? "信息采集表填写完成" : "表格填写存在问题: " + validation.getErrors())
                .generatedFiles(List.of(outputPath))
                .metadata(Map.of("validation", validation))
                .build();

        } catch (Exception e) {
            log.error("ReactFormFillAgent执行失败", e);
            return AgentResult.builder()
                .success(false)
                .message("表格填报失败: " + e.getMessage())
                .build();
        }
    }

    /**
     * 准备填充数据
     */
    private Map<String, Object> prepareFillData(CopyrightRequirement requirement) {
        Map<String, Object> data = new HashMap<>();

        // 基本信息
        data.put("SOFTWARE_NAME", requirement.getSoftwareName());
        data.put("SHORT_NAME", requirement.getShortName());
        data.put("VERSION", requirement.getVersion());
        data.put("CATEGORY", requirement.getCategory());
        data.put("LANGUAGE", requirement.getCodeLanguage());
        data.put("TECH_STACK", requirement.getTechStack());
        data.put("ARCHITECTURE", requirement.getArchitecture());
        data.put("DEV_COMPLETE_DATE", requirement.getDevCompleteDate());

        // 申请人信息
        data.put("APPLICANT_NAME", requirement.getApplicant().getName());
        data.put("APPLICANT_TYPE", requirement.getApplicant().getType());

        // 功能列表（动态表格）
        List<Map<String, String>> featureList = requirement.getFeatures().stream()
            .map(f -> Map.of(
                "FEATURE_NAME", f.getName(),
                "FEATURE_DESC", f.getDescription()
            ))
            .collect(Collectors.toList());
        data.put("FEATURES", featureList);

        // 创新点列表
        List<String> innovations = requirement.getInnovations();
        for (int i = 0; i < innovations.size(); i++) {
            data.put("INNOVATION_" + (i + 1), innovations.get(i));
        }

        return data;
    }
}

/**
 * POI工具类
 */
@Component
@Slf4j
public class PoiWordUtil {

    /**
     * 填充Word模板
     */
    public void fillWordTemplate(String templatePath, String outputPath, Map<String, Object> data)
            throws IOException {

        try (FileInputStream fis = new FileInputStream(templatePath);
             XWPFDocument document = new XWPFDocument(fis)) {

            // 1. 替换文档中的占位符
            replaceInParagraphs(document.getParagraphs(), data);

            // 2. 替换表格中的占位符
            for (XWPFTable table : document.getTables()) {
                replaceInTable(table, data);
            }

            // 3. 保存文档
            try (FileOutputStream fos = new FileOutputStream(outputPath)) {
                document.write(fos);
            }
        }
    }

    /**
     * 替换段落中的占位符
     */
    private void replaceInParagraphs(List<XWPFParagraph> paragraphs, Map<String, Object> data) {
        for (XWPFParagraph paragraph : paragraphs) {
            List<XWPFRun> runs = paragraph.getRuns();
            if (runs != null) {
                for (XWPFRun run : runs) {
                    String text = run.getText(0);
                    if (text != null) {
                        for (Map.Entry<String, Object> entry : data.entrySet()) {
                            String placeholder = "${" + entry.getKey() + "}";
                            if (text.contains(placeholder)) {
                                text = text.replace(placeholder, String.valueOf(entry.getValue()));
                            }
                        }
                        run.setText(text, 0);
                    }
                }
            }
        }
    }

    /**
     * 替换表格中的占位符（支持动态行）
     */
    private void replaceInTable(XWPFTable table, Map<String, Object> data) {
        // 处理静态字段替换
        for (XWPFTableRow row : table.getRows()) {
            for (XWPFTableCell cell : row.getTableCells()) {
                replaceInParagraphs(cell.getParagraphs(), data);
            }
        }

        // 处理动态表格（如功能列表）
        if (data.containsKey("FEATURES")) {
            @SuppressWarnings("unchecked")
            List<Map<String, String>> features = (List<Map<String, String>>) data.get("FEATURES");
            addDynamicTableRows(table, features, "${FEATURE_NAME}");
        }
    }

    /**
     * 动态添加表格行
     */
    private void addDynamicTableRows(XWPFTable table, List<Map<String, String>> rowData,
                                   String placeholder) {
        // 查找模板行
        int templateRowIndex = findTemplateRowIndex(table, placeholder);
        if (templateRowIndex == -1) return;

        XWPFTableRow templateRow = table.getRow(templateRowIndex);

        // 为每个数据项创建新行
        for (int i = 0; i < rowData.size(); i++) {
            XWPFTableRow newRow = (i == 0) ? templateRow : table.insertNewTableRow(templateRowIndex + i);

            // 填充行数据
            Map<String, String> data = rowData.get(i);
            for (int cellIndex = 0; cellIndex < newRow.getTableCells().size(); cellIndex++) {
                XWPFTableCell cell = newRow.getTableCells().get(cellIndex);
                for (XWPFParagraph paragraph : cell.getParagraphs()) {
                    for (XWPFRun run : paragraph.getRuns()) {
                        String text = run.getText(0);
                        if (text != null) {
                            for (Map.Entry<String, String> entry : data.entrySet()) {
                                String placeholderToReplace = "${" + entry.getKey() + "}";
                                text = text.replace(placeholderToReplace, entry.getValue());
                            }
                            run.setText(text, 0);
                        }
                    }
                }
            }
        }
    }
}
```

### 4.5 Agent 4: ReactDocWriterAgent（文档撰写）

```java
@Component
@Slf4j
public class ReactDocWriterAgent implements CopyrightAgent {

    @Autowired
    private ChatModel chatModel;

    @Autowired
    private McpClientUtil mcpClientUtil;

    @Override
    public AgentResult execute(AgentContext context) {
        try {
            CopyrightRequirement requirement = context.getRequirement();
            String workDir = context.getWorkDir();

            // 1. 生成Markdown文档内容
            String markdownContent = generateMarkdownDoc(requirement);

            // 2. 调用Office-Word-MCP转换为Word
            String outputFileName = "软著申报说明_" + context.getSessionId() + ".docx";
            String outputPath = Paths.get(workDir, outputFileName).toString();

            String wordFilePath = mcpClientUtil.generateFromMarkdown(markdownContent, outputPath);

            // 3. 设置仿宋字体
            mcpClientUtil.setDocumentFont(wordFilePath, "仿宋", 12);

            // 4. 验证文档格式
            DocumentValidationResult validation = validateDocument(wordFilePath);

            return AgentResult.builder()
                .success(validation.isValid())
                .message(validation.isValid() ? "申报说明文档生成完成" : "文档生成存在问题: " + validation.getErrors())
                .generatedFiles(List.of(wordFilePath))
                .metadata(Map.of("validation", validation, "wordCount", validation.getWordCount()))
                .build();

        } catch (Exception e) {
            log.error("ReactDocWriterAgent执行失败", e);
            return AgentResult.builder()
                .success(false)
                .message("文档撰写失败: " + e.getMessage())
                .build();
        }
    }

    /**
     * 生成Markdown文档内容
     */
    private String generateMarkdownDoc(CopyrightRequirement requirement) {
        String prompt = String.format("""
            请为以下软件编写详细的软件著作权申报说明文档，要求使用Markdown格式：

            软件信息：
            - 软件名称：%s
            - 版本号：%s
            - 技术架构：%s
            - 核心功能：%s
            - 创新点：%s

            文档要求：
            1. 包含完整的章节结构：软件概述、功能说明、技术架构、创新点、开发环境等
            2. 每个功能详细描述实现原理和用户价值
            3. 技术架构包含系统架构图的文字描述
            4. 创新点要突出技术特色和先进性
            5. 字数控制在3000-5000字
            6. 语言专业严谨，符合软著申报文档要求

            请生成专业的申报说明文档内容。
            """, requirement.getSoftwareName(), requirement.getVersion(),
            requirement.getArchitecture(),
            requirement.getFeatures().stream()
                .map(f -> f.getName() + "：" + f.getDescription())
                .collect(Collectors.joining("；")),
            String.join("；", requirement.getInnovations()));

        ChatResponse response = chatModel.call(new Prompt(prompt,
            ChatOptionsBuilder.builder()
                .temperature(0.4f)  // 适中的创造性
                .build()));

        return response.getResult().getOutput().getContent();
    }
}

/**
 * MCP客户端工具
 */
@Component
@Slf4j
public class McpClientUtil {

    @Value("${mcp.word-server.url:http://localhost:8765}")
    private String mcpServerUrl;

    @Autowired
    private RestTemplate restTemplate;

    /**
     * Markdown转Word文档
     */
    public String generateFromMarkdown(String markdownContent, String outputPath) {
        try {
            // 1. 创建MCP请求
            McpRequest request = McpRequest.builder()
                .method("generate_from_markdown")
                .params(Map.of(
                    "markdown_content", markdownContent,
                    "output_path", outputPath,
                    "title", "软件著作权申报说明"
                ))
                .build();

            // 2. 发送HTTP请求到MCP服务器
            ResponseEntity<McpResponse> response = restTemplate.postForEntity(
                mcpServerUrl + "/mcp/call",
                request,
                McpResponse.class
            );

            if (response.getStatusCode().is2xxSuccessful() && response.getBody().isSuccess()) {
                return response.getBody().getResult().toString();
            } else {
                throw new RuntimeException("MCP调用失败: " + response.getBody().getError());
            }

        } catch (Exception e) {
            log.error("MCP调用失败", e);
            throw new RuntimeException("Word文档生成失败: " + e.getMessage());
        }
    }

    /**
     * 设置文档字体
     */
    public void setDocumentFont(String filePath, String fontName, int fontSize) {
        try {
            McpRequest request = McpRequest.builder()
                .method("set_document_font")
                .params(Map.of(
                    "file_path", filePath,
                    "font_name", fontName,
                    "font_size", fontSize
                ))
                .build();

            ResponseEntity<McpResponse> response = restTemplate.postForEntity(
                mcpServerUrl + "/mcp/call",
                request,
                McpResponse.class
            );

            if (!response.getStatusCode().is2xxSuccessful() || !response.getBody().isSuccess()) {
                log.warn("字体设置失败: " + response.getBody().getError());
            }

        } catch (Exception e) {
            log.error("字体设置失败", e);
        }
    }
}
```

### 4.6 Agent 5: ReactQualityCheckAgent（质量检查）

```java
@Component
@Slf4j
public class ReactQualityCheckAgent implements CopyrightAgent {

    @Autowired
    private ChatModel chatModel;

    @Autowired
    private ToolCallback codeQualityTool;

    @Autowired
    private ToolCallback formValidationTool;

    @Autowired
    private ToolCallback documentCheckTool;

    /**
     * 创建ReactAgent实例
     */
    private ReactAgent createReactAgent() {
        return ReactAgent.builder()
            .name("质量检查Agent")
            .description("检查生成的软著申报材料质量，确保符合申报规范")
            .model(chatModel)
            .instruction("""
                你是一个专业的软件著作权申报质量检查专家。你需要检查三类文件：

                1. 源代码：
                   - 有效代码行数必须在5000-6000行之间
                   - 代码结构完整（实体、DAO、Service、Controller等）
                   - 代码质量良好，有适当注释

                2. 信息采集表：
                   - 所有必填字段已填写
                   - 数据格式正确
                   - 内容逻辑一致

                3. 申报说明文档：
                   - 使用仿宋字体、12号字
                   - 章节结构完整
                   - 内容详实，字数适中(3000-5000字)

                对于不符合要求的文件，请明确指出问题并给出修改建议。
                """)
            .tools(codeQualityTool, formValidationTool, documentCheckTool)
            .maxIterations(5)
            .build();
    }

    @Override
    public AgentResult execute(AgentContext context) {
        try {
            // 获取生成的文件
            List<String> generatedFiles = getGeneratedFiles(context.getSessionId());

            // 创建质检上下文
            QualityCheckContext checkContext = QualityCheckContext.builder()
                .sessionId(context.getSessionId())
                .files(generatedFiles)
                .requirement(context.getRequirement())
                .build();

            // 执行ReactAgent质量检查
            ReactAgent agent = createReactAgent();

            String prompt = String.format("""
                请检查以下软著申报材料的质量：

                会话ID：%s
                生成文件：%s

                请逐一检查每个文件是否符合软著申报规范，并给出详细的质检报告。
                """, context.getSessionId(), generatedFiles);

            String response = agent.call(prompt);

            // 解析质检结果
            QualityCheckReport report = parseQualityReport(response);

            return AgentResult.builder()
                .success(report.isAllPassed())
                .message(report.isAllPassed() ? "质量检查通过" : "质量检查不通过，存在问题需要修正")
                .data(report)
                .metadata(Map.of("checkDetails", report.getDetails()))
                .build();

        } catch (Exception e) {
            log.error("ReactQualityCheckAgent执行失败", e);
            return AgentResult.builder()
                .success(false)
                .message("质量检查失败: " + e.getMessage())
                .build();
        }
    }

}

/**
 * 质量检查工具配置类
 */
@Configuration
@Slf4j
class QualityCheckToolsConfig {

    /**
     * 代码质量检查工具
     */
    @Bean
    @Description("检查源代码质量，包括代码行数、结构完整性等")
    public ToolCallback codeQualityTool() {
        return FunctionToolCallback.builder("checkCodeQuality",
            (CodeQualityRequest request) -> {
                CodeQualityResponse response = new CodeQualityResponse();

                try {
                    // 1. 统计代码行数
                    int effectiveLines = countEffectiveCodeLines(request.getSourceCodePath());

                    // 2. 检查代码结构
                    boolean structureComplete = checkCodeStructure(request.getSourceCodePath());

                    // 3. 检查代码质量
                    List<String> qualityIssues = checkCodeQuality(request.getSourceCodePath());

                    response.setEffectiveLines(effectiveLines);
                    response.setLinesInRange(effectiveLines >= 5000 && effectiveLines <= 6000);
                    response.setStructureComplete(structureComplete);
                    response.setQualityIssues(qualityIssues);
                    response.setPassed(response.isLinesInRange() && structureComplete && qualityIssues.isEmpty());

                } catch (Exception e) {
                    response.setPassed(false);
                    response.setQualityIssues(List.of("代码检查失败: " + e.getMessage()));
                }

                return response;
            })
            .description("检查源代码质量，包括代码行数、结构完整性等")
            .inputType(CodeQualityRequest.class)
            .build();
    }

    /**
     * 表格验证工具
     */
    @Bean
    @Description("验证信息采集表的完整性和格式")
    public ToolCallback formValidationTool() {
        return FunctionToolCallback.builder("validateForm",
            (FormValidationRequest request) -> {
                FormValidationResponse response = new FormValidationResponse();

                try {
                    // 使用POI读取Word文档
                    List<String> missingFields = checkFormCompleteness(request.getFormPath());
                    List<String> formatErrors = checkFormFormat(request.getFormPath());

                    response.setMissingFields(missingFields);
                    response.setFormatErrors(formatErrors);
                    response.setPassed(missingFields.isEmpty() && formatErrors.isEmpty());

                } catch (Exception e) {
                    response.setPassed(false);
                    response.setFormatErrors(List.of("表格验证失败: " + e.getMessage()));
                }

                return response;
            })
            .description("验证信息采集表的完整性和格式")
            .inputType(FormValidationRequest.class)
            .build();
    }

    /**
     * 文档检查工具
     */
    @Bean
    @Description("检查申报说明文档的格式、字数和内容质量")
    public ToolCallback documentCheckTool() {
        return FunctionToolCallback.builder("checkDocument",
            (DocumentCheckRequest request) -> {
                DocumentCheckResponse response = new DocumentCheckResponse();

                try {
                    // 1. 检查字体格式
                    FontCheckResult fontCheck = checkDocumentFont(request.getDocPath());

                    // 2. 检查章节结构
                    boolean structureComplete = checkDocumentStructure(request.getDocPath());

                    // 3. 统计字数
                    int wordCount = countDocumentWords(request.getDocPath());

                    // 4. 检查内容质量
                    List<String> contentIssues = checkDocumentContent(request.getDocPath());

                    response.setFontCorrect(fontCheck.isCorrect());
                    response.setStructureComplete(structureComplete);
                    response.setWordCount(wordCount);
                    response.setWordCountInRange(wordCount >= 3000 && wordCount <= 5000);
                    response.setContentIssues(contentIssues);
                    response.setPassed(fontCheck.isCorrect() && structureComplete &&
                        response.isWordCountInRange() && contentIssues.isEmpty());

                } catch (Exception e) {
                    response.setPassed(false);
                    response.setContentIssues(List.of("文档检查失败: " + e.getMessage()));
                }

                return response;
            })
            .description("检查申报说明文档的格式、字数和内容质量")
            .inputType(DocumentCheckRequest.class)
            .build();
    }

    // 辅助方法
    private int countEffectiveCodeLines(String path) {
        // 实现代码行数统计
        return 0;
    }

    private boolean checkCodeStructure(String path) {
        // 实现代码结构检查
        return true;
    }

    private List<String> checkCodeQuality(String path) {
        // 实现代码质量检查
        return List.of();
    }

    private List<String> checkFormCompleteness(String path) {
        // 实现表格完整性检查
        return List.of();
    }

    private List<String> checkFormFormat(String path) {
        // 实现表格格式检查
        return List.of();
    }

    private FontCheckResult checkDocumentFont(String path) {
        // 实现字体检查
        return new FontCheckResult(true);
    }

    private boolean checkDocumentStructure(String path) {
        // 实现文档结构检查
        return true;
    }

    private int countDocumentWords(String path) {
        // 实现字数统计
        return 4000;
    }

    private List<String> checkDocumentContent(String path) {
        // 实现内容质量检查
        return List.of();
    }
}
```

---

## 五、Agent协作机制设计

### 5.1 编排器架构

```java
@Service
@Slf4j
public class CopyrightAgentOrchestrator {

    @Autowired
    private ReactClarifyAgent clarifyAgent;

    @Autowired
    private ReactCodeGenAgent codeGenAgent;

    @Autowired
    private ReactFormFillAgent formFillAgent;

    @Autowired
    private ReactDocWriterAgent docWriterAgent;

    @Autowired
    private ReactQualityCheckAgent qualityCheckAgent;

    @Autowired
    private AsyncTaskExecutor asyncTaskExecutor;

    /**
     * 编排Agent执行流程
     */
    @Async
    public CompletableFuture<OrchestratorResult> orchestrateAgents(String sessionId, String userId) {
        try {
            log.info("开始编排Agent执行流程，sessionId: {}", sessionId);

            // Phase 1: 需求澄清（如果还未完成）
            AgentContext context = buildAgentContext(sessionId, userId);
            if (context.getRequirement() == null) {
                log.info("需求尚未澄清完成，等待用户完善信息");
                return CompletableFuture.completedFuture(
                    OrchestratorResult.waiting("等待需求澄清完成"));
            }

            // Phase 2: 并行生成阶段
            updateSessionStatus(sessionId, SessionStatus.GENERATING);

            CompletableFuture<AgentResult> codeGenFuture = CompletableFuture
                .supplyAsync(() -> codeGenAgent.execute(context), asyncTaskExecutor);

            CompletableFuture<AgentResult> formFillFuture = CompletableFuture
                .supplyAsync(() -> formFillAgent.execute(context), asyncTaskExecutor);

            CompletableFuture<AgentResult> docWriterFuture = CompletableFuture
                .supplyAsync(() -> docWriterAgent.execute(context), asyncTaskExecutor);

            // 等待所有生成任务完成
            CompletableFuture<Void> allGenerationTasks = CompletableFuture.allOf(
                codeGenFuture, formFillFuture, docWriterFuture);

            allGenerationTasks.join(); // 阻塞等待

            // 检查生成结果
            AgentResult codeResult = codeGenFuture.get();
            AgentResult formResult = formFillFuture.get();
            AgentResult docResult = docWriterFuture.get();

            if (!codeResult.isSuccess() || !formResult.isSuccess() || !docResult.isSuccess()) {
                return CompletableFuture.completedFuture(
                    OrchestratorResult.failed("材料生成阶段失败"));
            }

            // Phase 3: 质量检查阶段
            updateSessionStatus(sessionId, SessionStatus.CHECKING);

            OrchestratorResult finalResult = executeQualityCheckLoop(context, 0);

            // Phase 4: 完成
            SessionStatus finalStatus = finalResult.isSuccess() ?
                SessionStatus.COMPLETED : SessionStatus.FAILED;
            updateSessionStatus(sessionId, finalStatus);

            return CompletableFuture.completedFuture(finalResult);

        } catch (Exception e) {
            log.error("Agent编排执行失败", e);
            updateSessionStatus(sessionId, SessionStatus.FAILED);
            return CompletableFuture.completedFuture(
                OrchestratorResult.failed("系统错误: " + e.getMessage()));
        }
    }

    /**
     * 质量检查循环（最多重试2次）
     */
    private OrchestratorResult executeQualityCheckLoop(AgentContext context, int retryCount) {
        if (retryCount > 2) {
            return OrchestratorResult.failed("质量检查重试次数已用尽，生成失败");
        }

        try {
            // 执行质量检查
            AgentResult checkResult = qualityCheckAgent.execute(context);

            if (checkResult.isSuccess()) {
                QualityCheckReport report = (QualityCheckReport) checkResult.getData();

                if (report.isAllPassed()) {
                    // 质检通过，返回成功
                    return OrchestratorResult.success("所有材料生成完成，质量检查通过",
                        getGeneratedFiles(context.getSessionId()));
                } else {
                    // 质检不通过，重新生成有问题的材料
                    log.warn("质量检查不通过，开始第{}次重新生成", retryCount + 1);

                    regenerateFailedComponents(context, report);

                    // 递归调用，重试质检
                    return executeQualityCheckLoop(context, retryCount + 1);
                }
            } else {
                return OrchestratorResult.failed("质量检查执行失败: " + checkResult.getMessage());
            }

        } catch (Exception e) {
            log.error("质量检查循环执行失败", e);
            return OrchestratorResult.failed("质量检查失败: " + e.getMessage());
        }
    }

    /**
     * 重新生成失败的组件
     */
    private void regenerateFailedComponents(AgentContext context, QualityCheckReport report) {
        List<CompletableFuture<Void>> regenerationTasks = new ArrayList<>();

        // 根据质检报告决定重新生成哪些组件
        if (!report.getCodeCheck().isPassed()) {
            regenerationTasks.add(CompletableFuture.runAsync(() -> {
                log.info("重新生成代码");
                codeGenAgent.execute(context);
            }, asyncTaskExecutor));
        }

        if (!report.getFormCheck().isPassed()) {
            regenerationTasks.add(CompletableFuture.runAsync(() -> {
                log.info("重新生成表格");
                formFillAgent.execute(context);
            }, asyncTaskExecutor));
        }

        if (!report.getDocCheck().isPassed()) {
            regenerationTasks.add(CompletableFuture.runAsync(() -> {
                log.info("重新生成文档");
                docWriterAgent.execute(context);
            }, asyncTaskExecutor));
        }

        // 等待所有重新生成任务完成
        CompletableFuture.allOf(regenerationTasks.toArray(new CompletableFuture[0])).join();
    }
}

/**
 * 编排器结果
 */
@Data
@Builder
public class OrchestratorResult {
    private boolean success;
    private String message;
    private List<String> generatedFiles;
    private QualityCheckReport qualityReport;
    private OrchestratorStatus status;

    public static OrchestratorResult success(String message, List<String> files) {
        return OrchestratorResult.builder()
            .success(true)
            .message(message)
            .generatedFiles(files)
            .status(OrchestratorStatus.COMPLETED)
            .build();
    }

    public static OrchestratorResult failed(String message) {
        return OrchestratorResult.builder()
            .success(false)
            .message(message)
            .status(OrchestratorStatus.FAILED)
            .build();
    }

    public static OrchestratorResult waiting(String message) {
        return OrchestratorResult.builder()
            .success(false)
            .message(message)
            .status(OrchestratorStatus.WAITING)
            .build();
    }
}
```

### 5.2 异步事件驱动

```java
/**
 * Agent事件发布
 */
@Component
@Slf4j
public class AgentEventPublisher {

    @Autowired
    private ApplicationEventPublisher eventPublisher;

    /**
     * 发布Agent开始执行事件
     */
    public void publishAgentStarted(String sessionId, String agentName) {
        AgentExecutionEvent event = AgentExecutionEvent.builder()
            .sessionId(sessionId)
            .agentName(agentName)
            .status(AgentExecutionStatus.STARTED)
            .timestamp(LocalDateTime.now())
            .build();
        eventPublisher.publishEvent(event);
    }

    /**
     * 发布Agent执行完成事件
     */
    public void publishAgentCompleted(String sessionId, String agentName, AgentResult result) {
        AgentExecutionEvent event = AgentExecutionEvent.builder()
            .sessionId(sessionId)
            .agentName(agentName)
            .status(result.isSuccess() ? AgentExecutionStatus.COMPLETED : AgentExecutionStatus.FAILED)
            .result(result)
            .timestamp(LocalDateTime.now())
            .build();
        eventPublisher.publishEvent(event);
    }
}

/**
 * Agent事件监听器
 */
@Component
@Slf4j
public class AgentEventListener {

    @Autowired
    private CopyrightChatWebSocket webSocketHandler;

    @Autowired
    private CopyrightSessionService sessionService;

    /**
     * 监听Agent执行事件，实时推送给前端
     */
    @EventListener
    @Async
    public void handleAgentExecutionEvent(AgentExecutionEvent event) {
        try {
            // 1. 更新数据库状态
            updateSessionProgress(event.getSessionId(), event);

            // 2. 构建WebSocket消息
            WebSocketMessage wsMessage = WebSocketMessage.builder()
                .type("agent_status")
                .sessionId(event.getSessionId())
                .data(Map.of(
                    "agentName", event.getAgentName(),
                    "status", event.getStatus().name(),
                    "message", buildStatusMessage(event),
                    "timestamp", event.getTimestamp()
                ))
                .build();

            // 3. 推送给前端
            webSocketHandler.sendMessageToSession(event.getSessionId(), wsMessage);

        } catch (Exception e) {
            log.error("处理Agent执行事件失败", e);
        }
    }

    private String buildStatusMessage(AgentExecutionEvent event) {
        switch (event.getStatus()) {
            case STARTED:
                return getAgentStartMessage(event.getAgentName());
            case COMPLETED:
                return getAgentCompleteMessage(event.getAgentName());
            case FAILED:
                return getAgentFailMessage(event.getAgentName());
            default:
                return "Agent状态更新";
        }
    }

    private String getAgentStartMessage(String agentName) {
        switch (agentName) {
            case "ReactClarifyAgent": return "正在澄清需求信息...";
            case "ReactCodeGenAgent": return "正在生成源代码...";
            case "ReactFormFillAgent": return "正在填写信息采集表...";
            case "ReactDocWriterAgent": return "正在撰写申报说明文档...";
            case "ReactQualityCheckAgent": return "正在进行质量检查...";
            default: return "Agent " + agentName + " 开始执行";
        }
    }
}
```

---

## 六、额外功能设计

### 6.1 MCP集成架构

```java
/**
 * MCP配置
 */
@Configuration
public class McpConfig {

    @Value("${mcp.word-server.url}")
    private String mcpServerUrl;

    @Value("${mcp.word-server.timeout:30000}")
    private int timeout;

    @Bean
    public RestTemplate mcpRestTemplate() {
        RestTemplate restTemplate = new RestTemplate();

        // 设置超时
        HttpComponentsClientHttpRequestFactory requestFactory =
            new HttpComponentsClientHttpRequestFactory();
        requestFactory.setConnectTimeout(timeout);
        requestFactory.setReadTimeout(timeout);
        restTemplate.setRequestFactory(requestFactory);

        // 设置错误处理器
        restTemplate.setErrorHandler(new McpErrorHandler());

        return restTemplate;
    }
}

/**
 * MCP健康检查
 */
@Component
@Slf4j
public class McpHealthChecker {

    @Autowired
    private RestTemplate mcpRestTemplate;

    @Value("${mcp.word-server.url}")
    private String mcpServerUrl;

    /**
     * 检查MCP服务器健康状态
     */
    @Scheduled(fixedRate = 60000) // 每分钟检查一次
    public void checkMcpHealth() {
        try {
            ResponseEntity<Map> response = mcpRestTemplate.getForEntity(
                mcpServerUrl + "/health", Map.class);

            if (response.getStatusCode().is2xxSuccessful()) {
                log.debug("MCP服务器健康状态良好");
            } else {
                log.warn("MCP服务器健康检查异常: {}", response.getStatusCode());
            }

        } catch (Exception e) {
            log.error("MCP服务器健康检查失败", e);
            // 可以在这里实现告警机制
        }
    }
}
```

### 6.2 文件下载优化

```java
/**
 * 文件下载服务
 */
@Service
@Slf4j
public class FileDownloadService {

    @Autowired
    private CopyrightFileService fileService;

    /**
     * 流式下载大文件
     */
    public void streamDownload(String sessionId, String fileType, HttpServletResponse response) {
        try {
            // 1. 查找文件
            CopyrightFile file = fileService.findBySessionAndType(sessionId, fileType);
            if (file == null) {
                throw new FileNotFoundException("文件不存在");
            }

            File sourceFile = new File(file.getFilePath());
            if (!sourceFile.exists()) {
                throw new FileNotFoundException("源文件不存在: " + file.getFilePath());
            }

            // 2. 设置响应头
            response.setContentType(getContentType(file.getFilename()));
            response.setContentLengthLong(sourceFile.length());
            response.setHeader("Content-Disposition",
                "attachment; filename=" + URLEncoder.encode(file.getFilename(), StandardCharsets.UTF_8));

            // 3. 流式传输
            try (FileInputStream fis = new FileInputStream(sourceFile);
                 BufferedInputStream bis = new BufferedInputStream(fis);
                 OutputStream os = response.getOutputStream()) {

                byte[] buffer = new byte[8192];
                int bytesRead;
                while ((bytesRead = bis.read(buffer)) != -1) {
                    os.write(buffer, 0, bytesRead);
                }
                os.flush();
            }

        } catch (Exception e) {
            log.error("文件下载失败: sessionId={}, fileType={}", sessionId, fileType, e);
            throw new RuntimeException("文件下载失败: " + e.getMessage());
        }
    }

    /**
     * 批量打包下载
     */
    public void downloadAllFiles(String sessionId, HttpServletResponse response) {
        try {
            List<CopyrightFile> files = fileService.findBySession(sessionId);
            if (files.isEmpty()) {
                throw new RuntimeException("该会话无可下载文件");
            }

            String zipFileName = "软著申报材料_" + sessionId + ".zip";
            response.setContentType("application/zip");
            response.setHeader("Content-Disposition",
                "attachment; filename=" + URLEncoder.encode(zipFileName, StandardCharsets.UTF_8));

            // 使用ZipOutputStream直接写入响应流
            try (ZipOutputStream zos = new ZipOutputStream(response.getOutputStream())) {
                for (CopyrightFile file : files) {
                    addFileToZip(zos, file);
                }
            }

        } catch (Exception e) {
            log.error("批量下载失败: sessionId={}", sessionId, e);
            throw new RuntimeException("批量下载失败: " + e.getMessage());
        }
    }

    private void addFileToZip(ZipOutputStream zos, CopyrightFile file) throws IOException {
        File sourceFile = new File(file.getFilePath());
        if (!sourceFile.exists()) {
            return;
        }

        ZipEntry entry = new ZipEntry(file.getFilename());
        entry.setSize(sourceFile.length());
        entry.setTime(sourceFile.lastModified());

        zos.putNextEntry(entry);

        try (FileInputStream fis = new FileInputStream(sourceFile)) {
            byte[] buffer = new byte[8192];
            int len;
            while ((len = fis.read(buffer)) > 0) {
                zos.write(buffer, 0, len);
            }
        }

        zos.closeEntry();
    }
}
```

### 6.3 系统监控和日志

```java
/**
 * 系统监控
 */
@Component
@Slf4j
public class SystemMonitor {

    @Autowired
    private MeterRegistry meterRegistry;

    // 会话计数器
    private final Counter sessionCounter = Counter.builder("copyright.session.created")
        .description("软著申报会话创建数量")
        .register(meterRegistry);

    // Agent执行时间
    private final Timer agentTimer = Timer.builder("copyright.agent.execution")
        .description("Agent执行时间")
        .register(meterRegistry);

    // 文件下载计数
    private final Counter downloadCounter = Counter.builder("copyright.file.download")
        .description("文件下载次数")
        .register(meterRegistry);

    /**
     * 记录会话创建
     */
    public void recordSessionCreated(String userId, String sessionType) {
        sessionCounter.increment(
            Tags.of("user", userId, "type", sessionType)
        );
    }

    /**
     * 记录Agent执行时间
     */
    public void recordAgentExecution(String agentName, Duration duration, boolean success) {
        agentTimer.record(duration,
            Tags.of("agent", agentName, "success", String.valueOf(success))
        );
    }

    /**
     * 记录文件下载
     */
    public void recordFileDownload(String fileType, long fileSize) {
        downloadCounter.increment(
            Tags.of("type", fileType, "size_mb", String.valueOf(fileSize / 1024 / 1024))
        );
    }
}

/**
 * 业务日志记录
 */
@Aspect
@Component
@Slf4j
public class BusinessLogAspect {

    /**
     * Agent执行日志
     */
    @Around("@annotation(LogAgentExecution)")
    public Object logAgentExecution(ProceedingJoinPoint joinPoint) throws Throwable {
        String agentName = joinPoint.getTarget().getClass().getSimpleName();
        Object[] args = joinPoint.getArgs();
        String sessionId = null;

        if (args.length > 0 && args[0] instanceof AgentContext) {
            sessionId = ((AgentContext) args[0]).getSessionId();
        }

        long startTime = System.currentTimeMillis();

        try {
            log.info("Agent开始执行: agent={}, sessionId={}", agentName, sessionId);

            Object result = joinPoint.proceed();

            long duration = System.currentTimeMillis() - startTime;
            log.info("Agent执行完成: agent={}, sessionId={}, duration={}ms",
                agentName, sessionId, duration);

            return result;

        } catch (Exception e) {
            long duration = System.currentTimeMillis() - startTime;
            log.error("Agent执行失败: agent={}, sessionId={}, duration={}ms, error={}",
                agentName, sessionId, duration, e.getMessage(), e);
            throw e;
        }
    }
}
```

---

## 七、数据库设计优化

### 7.1 完整表结构

```sql
-- 1. 会话表
CREATE TABLE copyright_session (
    id VARCHAR(32) PRIMARY KEY COMMENT '会话ID',
    user_id VARCHAR(32) NOT NULL COMMENT '用户ID',
    software_name VARCHAR(255) COMMENT '软件名称',
    status VARCHAR(20) NOT NULL DEFAULT 'CLARIFYING' COMMENT '状态：CLARIFYING/GENERATING/CHECKING/COMPLETED/FAILED',
    requirement_json TEXT COMMENT '需求JSON',
    progress_json TEXT COMMENT '进度JSON',
    error_message TEXT COMMENT '错误信息',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time)
) COMMENT '软著申报会话表';

-- 2. 对话记录表
CREATE TABLE copyright_message (
    id VARCHAR(32) PRIMARY KEY COMMENT '消息ID',
    session_id VARCHAR(32) NOT NULL COMMENT '会话ID',
    role VARCHAR(20) NOT NULL COMMENT '角色：user/assistant/system',
    content TEXT NOT NULL COMMENT '消息内容',
    message_type VARCHAR(20) DEFAULT 'text' COMMENT '消息类型：text/file/status',
    metadata_json TEXT COMMENT '消息元数据JSON',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_session_id (session_id),
    INDEX idx_create_time (create_time),
    FOREIGN KEY (session_id) REFERENCES copyright_session(id) ON DELETE CASCADE
) COMMENT '软著申报对话记录表';

-- 3. 生成文件表
CREATE TABLE copyright_file (
    id VARCHAR(32) PRIMARY KEY COMMENT '文件ID',
    session_id VARCHAR(32) NOT NULL COMMENT '会话ID',
    file_type VARCHAR(20) NOT NULL COMMENT '文件类型：source_code/info_form/desc_doc',
    filename VARCHAR(255) NOT NULL COMMENT '文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
    file_size BIGINT COMMENT '文件大小（字节）',
    mime_type VARCHAR(100) COMMENT 'MIME类型',
    quality_status VARCHAR(20) DEFAULT 'checking' COMMENT '质量状态：checking/passed/failed',
    quality_report_json TEXT COMMENT '质检报告JSON',
    version INT DEFAULT 1 COMMENT '文件版本号',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_session_id (session_id),
    INDEX idx_file_type (file_type),
    INDEX idx_quality_status (quality_status),
    UNIQUE KEY uk_session_type_version (session_id, file_type, version),
    FOREIGN KEY (session_id) REFERENCES copyright_session(id) ON DELETE CASCADE
) COMMENT '软著申报生成文件表';

-- 4. Agent执行记录表
CREATE TABLE copyright_agent_log (
    id VARCHAR(32) PRIMARY KEY COMMENT '日志ID',
    session_id VARCHAR(32) NOT NULL COMMENT '会话ID',
    agent_name VARCHAR(100) NOT NULL COMMENT 'Agent名称',
    status VARCHAR(20) NOT NULL COMMENT '执行状态：STARTED/COMPLETED/FAILED',
    start_time DATETIME COMMENT '开始时间',
    end_time DATETIME COMMENT '结束时间',
    duration_ms BIGINT COMMENT '执行时长（毫秒）',
    input_params JSON COMMENT '输入参数',
    output_result JSON COMMENT '输出结果',
    error_message TEXT COMMENT '错误信息',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_session_id (session_id),
    INDEX idx_agent_name (agent_name),
    INDEX idx_status (status),
    INDEX idx_start_time (start_time),
    FOREIGN KEY (session_id) REFERENCES copyright_session(id) ON DELETE CASCADE
) COMMENT 'Agent执行日志表';

-- 5. 系统配置表
CREATE TABLE copyright_config (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '配置ID',
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    config_value TEXT NOT NULL COMMENT '配置值',
    config_type VARCHAR(20) DEFAULT 'string' COMMENT '配置类型：string/int/bool/json',
    description VARCHAR(255) COMMENT '配置描述',
    is_system TINYINT(1) DEFAULT 0 COMMENT '是否系统配置',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT '系统配置表';

-- 初始化系统配置
INSERT INTO copyright_config (config_key, config_value, config_type, description, is_system) VALUES
('agent.clarify.max_iterations', '10', 'int', '需求澄清Agent最大对话轮次', 1),
('agent.quality.max_retries', '2', 'int', '质量检查最大重试次数', 1),
('file.storage.base_path', '/data/copyright-files', 'string', '文件存储基础路径', 1),
('mcp.word_server.url', 'http://localhost:8765', 'string', 'MCP Word服务器地址', 1),
('code.target_lines.min', '5000', 'int', '目标代码最小行数', 1),
('code.target_lines.max', '6000', 'int', '目标代码最大行数', 1);
```

### 7.2 性能优化索引

```sql
-- 会话列表查询优化
CREATE INDEX idx_session_user_status_time ON copyright_session(user_id, status, create_time DESC);

-- 消息历史查询优化
CREATE INDEX idx_message_session_time ON copyright_message(session_id, create_time ASC);

-- 文件查询优化
CREATE INDEX idx_file_session_type_quality ON copyright_file(session_id, file_type, quality_status);

-- Agent日志分析优化
CREATE INDEX idx_agent_log_name_time ON copyright_agent_log(agent_name, start_time DESC);
```

---

## 八、部署配置

### 8.1 Docker Compose部署

```yaml
# docker-compose.yml
version: '3.8'
services:
  copyright-app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - SPRING_DATASOURCE_URL=jdbc:mysql://mysql:3306/jeecg_boot?useSSL=false&serverTimezone=Asia/Shanghai
      - SPRING_DATASOURCE_USERNAME=root
      - SPRING_DATASOURCE_PASSWORD=${DB_PASSWORD}
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
      - MCP_WORD_SERVER_URL=http://mcp-word-server:8765
    volumes:
      - ./data/copyright-files:/data/copyright-files
    depends_on:
      - mysql
      - redis
      - mcp-word-server
    networks:
      - copyright-network

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${DB_PASSWORD}
      - MYSQL_DATABASE=jeecg_boot
    volumes:
      - mysql-data:/var/lib/mysql
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    networks:
      - copyright-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    networks:
      - copyright-network

  mcp-word-server:
    build: ./Office-Word-MCP-Server
    ports:
      - "8765:8765"
    command: ["python", "word_mcp_server.py", "--transport", "sse", "--port", "8765"]
    volumes:
      - ./data/mcp-temp:/app/temp
    networks:
      - copyright-network

volumes:
  mysql-data:
  redis-data:

networks:
  copyright-network:
    driver: bridge
```

### 8.2 生产环境配置

```yaml
# application-prod.yml
server:
  port: 8080
  servlet:
    context-path: /copyright

spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: ${SPRING_DATASOURCE_URL}
    username: ${SPRING_DATASOURCE_USERNAME}
    password: ${SPRING_DATASOURCE_PASSWORD}
    type: com.alibaba.druid.pool.DruidDataSource
    druid:
      initial-size: 5
      min-idle: 5
      max-active: 20
      max-wait: 60000
      pool-prepared-statements: true
      max-pool-prepared-statement-per-connection-size: 20

  ai:
    dashscope:
      api-key: ${DASHSCOPE_API_KEY}
      chat:
        options:
          model: qwen-max
          temperature: 0.7
          max-tokens: 4000

  task:
    execution:
      pool:
        core-size: 8
        max-size: 16
        queue-capacity: 100
        thread-name-prefix: "copyright-agent-"

# 业务配置
copyright:
  storage:
    base-path: /data/copyright-files
    max-file-size: 100MB
    allowed-extensions: [".java", ".py", ".docx", ".zip"]

  agent:
    clarify:
      max-iterations: 10
      timeout: 300000
    quality-check:
      max-retries: 2
      timeout: 600000

  mcp:
    word-server:
      url: ${MCP_WORD_SERVER_URL}
      timeout: 30000
      health-check-interval: 60000

# 监控配置
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
  endpoint:
    health:
      show-details: always

# 日志配置
logging:
  level:
    org.jeecg.modules.copyright: INFO
    com.alibaba.cloud.ai: DEBUG
  file:
    name: /var/log/copyright/app.log
  pattern:
    file: "%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n"
```

---

## 九、总结

这个详细设计文档涵盖了软著申报AI系统的完整设计，包括：

### ✅ 已完成设计的功能

1. **用户对话页面**: 支持多用户、多会话、实时通信、文件管理
2. **申报记录管理**: 完整的查询、详情、下载功能
3. **5个Agent设计**: 详细的功能实现和协作机制
4. **Agent协作流程**: 编排器、事件驱动、质量检查循环
5. **额外功能**: MCP集成、文件下载、监控日志

### 🏗️ 核心技术亮点

- **ReactAgent + 普通Agent混合模式**: 兼顾智能推理和执行效率
- **并行执行 + 质量检查循环**: 保证生成质量和系统可靠性
- **事件驱动架构**: 实时状态更新和进度推送
- **完整的监控体系**: 业务监控、性能监控、日志追踪

### 📋 下一步行动

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"activeForm": "\u7f16\u5199\u5b8c\u6574\u7684\u7cfb\u7edf\u8bbe\u8ba1\u6587\u6863", "content": "\u7f16\u5199\u5b8c\u6574\u7684\u7cfb\u7edf\u8bbe\u8ba1\u6587\u6863", "status": "completed"}]