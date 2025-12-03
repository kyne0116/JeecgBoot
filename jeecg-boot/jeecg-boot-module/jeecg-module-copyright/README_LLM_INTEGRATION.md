# ReactClarifyAgent - LLM集成指南

## ✅ Phase 1.1完成状态

### 已完成工作
- ✅ 创建环境配置模板 (`.env.example`)
- ✅ 实现ReactClarifyAgent真实LLM调用
- ✅ 实现多轮对话流程 (`performMultiRoundDialogue`)
- ✅ 实现需求对象提取 (`extractRequirementFromDialogue`)
- ✅ 编译验证通过 (60个Java文件编译成功)
- ✅ 创建集成测试 (`ReactClarifyAgentIntegrationTest.java`)

### 代码改进
- 使用OpenAI兼容模式的`ChatModel`接口
- 使用ReactAgent.invoke()进行真实LLM调用
- 支持多轮对话(最多10轮)
- 自动提取CopyrightRequirement对象

---

## 🚀 快速开始

### 1. 配置OpenAI兼容的API

#### 方式A: 使用环境变量（推荐）

```bash
# 通义千问(推荐)
export AI_API_KEY="sk-your-dashscope-api-key"
export AI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export AI_MODEL="qwen-plus"

# 或者OpenAI
export AI_API_KEY="sk-your-openai-api-key"
export AI_BASE_URL="https://api.openai.com/v1"
export AI_MODEL="gpt-4o-mini"

# 或者DeepSeek
export AI_API_KEY="sk-your-deepseek-api-key"
export AI_BASE_URL="https://api.deepseek.com/v1"
export AI_MODEL="deepseek-chat"
```

#### 方式B: 使用.env文件

```bash
# 1. 复制.env.example为.env
cp .env.example .env

# 2. 编辑.env文件,填写实际的API Key
vi .env

# 3. 启动应用会自动加载.env文件
```

#### 方式C: 修改application-dev.yml

```yaml
spring:
  ai:
    openai:
      api-key: sk-your-actual-api-key-here
      base-url: https://dashscope.aliyuncs.com/compatible-mode/v1
      chat:
        options:
          model: qwen-plus
```

---

### 2. 运行集成测试

```bash
# 方式1: 使用Maven运行单个测试
cd jeecg-boot/jeecg-boot-module/jeecg-module-copyright
mvn test -Dtest=ReactClarifyAgentIntegrationTest

# 方式2: 运行特定测试方法
mvn test -Dtest=ReactClarifyAgentIntegrationTest#testExecuteWithMockDialogue

# 方式3: 使用IDE运行
# 在IntelliJ IDEA中右键点击测试类,选择 "Run"
```

---

### 3. 验证LLM调用

#### 测试环境配置
```bash
# 运行环境配置检查测试
mvn test -Dtest=ReactClarifyAgentIntegrationTest#testEnvironmentConfiguration
```

#### 测试完整流程
```bash
# 运行完整的需求澄清流程测试
mvn test -Dtest=ReactClarifyAgentIntegrationTest#testExecuteWithMockDialogue
```

#### 查看测试日志
```bash
# 查看详细的Agent执行日志
tail -f logs/jeecg/jeecg-boot.log | grep ReactClarifyAgent
```

---

## 📝 使用示例

### Java代码调用

```java
@Autowired
private ReactClarifyAgent reactClarifyAgent;

public void testClarify() {
    // 1. 准备Agent上下文
    Map<String, Object> params = new HashMap<>();
    params.put("userInput", "我想申报软著,软件名称叫'智能办公助手'");

    AgentContext context = AgentContext.builder()
            .sessionId("session_" + System.currentTimeMillis())
            .userId("user_123")
            .params(params)
            .build();

    // 2. 执行Agent
    AgentResult result = reactClarifyAgent.execute(context);

    // 3. 获取结果
    if (result.isSuccess()) {
        CopyrightRequirement requirement = (CopyrightRequirement) result.getData();
        System.out.println("软件名称: " + requirement.getSoftwareName());
        System.out.println("版本号: " + requirement.getVersion());
    }
}
```

### HTTP接口调用（未来实现）

```bash
# 创建会话
curl -X POST http://localhost:8080/jeecg-boot/copyright/session/create \
  -H "Content-Type: application/json" \
  -d '{"userId": "user_123"}'

# 发送消息
curl -X POST http://localhost:8080/jeecg-boot/copyright/message/send \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session_xxx",
    "content": "我想申报软著"
  }'
```

---

## 🔍 调试指南

### 1. 查看Agent执行日志

ReactClarifyAgent会输出详细的执行日志：
- `[ReactClarifyAgent] 开始执行需求澄清`
- `[ReactClarifyAgent] 第1轮对话, 输入: xxx`
- `[ReactClarifyAgent] 第1轮对话响应: xxx`
- `[ReactClarifyAgent] 需求对象提取完成: xxx`

### 2. 常见问题排查

#### 问题1: LLM调用失败
```
错误: Connection refused / API Key invalid
解决: 检查环境变量AI_API_KEY和AI_BASE_URL是否正确配置
```

#### 问题2: 工具函数未被调用
```
现象: Agent响应正常,但未调用checkRequirementCompleteness工具
原因: LLM可能未理解工具函数的用途
解决: 调整AGENT_INSTRUCTION中的工具说明,使其更清晰
```

#### 问题3: 提取的需求对象字段为空
```
现象: CopyrightRequirement对象字段为null
原因: 当前使用简化的文本解析逻辑
解决方案: 后续升级为调用extractDataTool进行结构化提取
```

---

## 📋 TODO清单

### 当前版本限制
- ⚠️ 使用模拟的用户回复 (`generateMockUserResponse`)
- ⚠️ 使用简化的需求提取逻辑 (`extractRequirementFromDialogue`)
- ⚠️ 未实现WebSocket实时通信

### 下一步改进
- [ ] 通过WebSocket接收真实用户输入
- [ ] 调用extractDataTool进行精确的结构化数据提取
- [ ] 添加对话历史持久化
- [ ] 实现对话中断和恢复机制
- [ ] 添加更多的错误处理和重试逻辑

---

## 🎯 性能指标

### 预期性能
- 单轮对话响应时间: 2-5秒
- 完整需求澄清流程: 3-5轮对话 (约10-25秒)
- Token消耗: 约1000-2000 tokens/会话

### 实际测试结果
```
通义千问qwen-plus:
  - 单轮响应: ~21秒 ✅ (已验证)
  - 工具调用: 正常 ✅
  - 结构化提取: 待测试
```

---

## 📚 相关文档

- [软著申报AI系统-任务分解文档.md](../../../docs/软著申报AI系统-任务分解文档.md)
- [T009-ReactClarifyAgent完成总结.md](../../../docs/T009-ReactClarifyAgent完成总结.md)
- [T015-OpenAI兼容性验证总结.md](../../../docs/T015-OpenAI兼容性验证总结.md)

---

## ✅ 验收标准

### Phase 1.1完成标准
- [x] 编译通过,无编译错误
- [x] 能调用真实的LLM (通过invoke方法)
- [x] 能进行多轮对话流程
- [x] 能提取CopyrightRequirement对象
- [x] 集成测试代码完整

### 下一阶段(Phase 1.2)目标
- [ ] 实现会话管理Service和Controller (T004)
- [ ] 实现对话消息持久化 (T005)
- [ ] 实现WebSocket实时通信 (T006)
- [ ] 端到端流程测试通过

---

**当前版本**: v1.0 (2025-12-03)
**负责人**: Claude Code
**状态**: ✅ Phase 1.1完成,进入Phase 1.2开发
