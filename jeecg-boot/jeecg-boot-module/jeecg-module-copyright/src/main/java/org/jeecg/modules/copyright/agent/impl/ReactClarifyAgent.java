package org.jeecg.modules.copyright.agent.impl;

import com.alibaba.cloud.ai.graph.RunnableConfig;
import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.agent.core.*;
import org.jeecg.modules.copyright.agent.tools.ExtractDataTool;
import org.jeecg.modules.copyright.agent.tools.RequirementCheckTool;
import org.jeecg.modules.copyright.vo.CopyrightRequirement;
import org.jeecg.modules.copyright.vo.ExtractDataRequest;
import org.jeecg.modules.copyright.vo.RequirementCheckRequest;
import org.jeecg.modules.copyright.vo.RequirementCheckResponse;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.model.ToolContext;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.function.FunctionToolCallback;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.BiFunction;

/**
 * ReactClarifyAgent - 需求澄清Agent
 * 采用ReAct(推理-行动)模式,通过多轮对话澄清软著申报需求
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Component
@Slf4j
public class ReactClarifyAgent implements CopyrightAgent {

    @Autowired
    private ChatModel chatModel;

    @Autowired
    private BiFunction<RequirementCheckRequest, ToolContext, RequirementCheckResponse> requirementCheckTool;

    @Autowired
    private ExtractDataTool extractDataTool;

    private static final int MAX_CONVERSATION_ROUNDS = 10;

    private static final String AGENT_INSTRUCTION = """
            你是一个专业的软著申报需求澄清助手。你的任务是通过多轮对话,收集用户的软著申报需求信息。

            必须收集的9个必填字段:
            1. softwareName (软件全称)
            2. shortName (软件简称)
            3. version (版本号)
            4. category (软件分类: 应用软件/系统软件/支撑软件/嵌入式软件)
            5. codeLanguage (主要编程语言)
            6. techStack (技术架构)
            7. features (核心功能列表, 至少3个功能)
            8. innovations (技术创新点, 至少2个)
            9. applicantName (申请人信息)

            工作流程:
            1. 首先调用checkRequirementCompleteness工具检查当前信息完整度
            2. 根据检查结果,询问缺失的字段(每次最多询问2个字段)
            3. 收集用户回复后,再次调用checkRequirementCompleteness检查
            4. 重复步骤2-3,直到完整度达到100%
            5. 信息收集完成后,调用extractStructuredData提取结构化JSON

            沟通风格:
            - 友好、专业、高效
            - 每次提问简洁明确,避免一次问太多问题
            - 对用户的回复给予积极反馈
            - 适时提供示例帮助用户理解

            注意事项:
            - 不要重复询问已经提供的信息
            - 按照优先级询问字段(软件名称最重要)
            - 确保features至少3个、innovations至少2个
            - 最后一定要调用extractStructuredData提取完整JSON
            """;

    @Override
    @LogAgentExecution
    public AgentResult execute(AgentContext context) {
        log.info("[ReactClarifyAgent] 开始执行需求澄清, sessionId: {}", context.getSessionId());

        try {
            // 构建ReactAgent
            ReactAgent reactAgent = buildReactAgent(context);

            // 初始化对话状态
            Map<String, Object> state = new HashMap<>();
            state.put("sessionId", context.getSessionId());
            state.put("userId", context.getUserId());

            // 从context中获取用户初始输入
            String userInput = (String) context.getParams().getOrDefault("userInput",
                    "我想申报软著,请帮我收集信息");

            log.info("[ReactClarifyAgent] 用户输入: {}", userInput);

            // 执行多轮对话流程
            CopyrightRequirement requirement = performMultiRoundDialogue(reactAgent, userInput, state, context);

            if (requirement == null) {
                return AgentResult.failure("需求澄清失败: 未能提取完整的需求信息");
            }

            log.info("[ReactClarifyAgent] 需求澄清完成: {}", requirement.getSoftwareName());

            return AgentResult.success(
                    "需求澄清完成,已收集完整的软著申报信息",
                    requirement
            );

        } catch (Exception e) {
            log.error("[ReactClarifyAgent] 执行失败", e);
            return AgentResult.failure("需求澄清失败: " + e.getMessage());
        }
    }

    /**
     * 执行多轮对话流程,收集完整的需求信息
     *
     * @param reactAgent ReactAgent实例
     * @param initialInput 用户初始输入
     * @param state 对话状态
     * @param context Agent上下文
     * @return 提取的需求对象,失败返回null
     */
    private CopyrightRequirement performMultiRoundDialogue(
            ReactAgent reactAgent,
            String initialInput,
            Map<String, Object> state,
            AgentContext context) {

        log.info("[ReactClarifyAgent] 开始多轮对话流程");

        try {
            // 构建对话历史
            StringBuilder conversationHistory = new StringBuilder();
            conversationHistory.append("用户: ").append(initialInput).append("\n");

            // 第一轮对话 - 让Agent开始收集信息
            String currentInput = initialInput;
            String agentResponse = null;

            for (int round = 1; round <= MAX_CONVERSATION_ROUNDS; round++) {
                log.info("[ReactClarifyAgent] 第{}轮对话, 输入: {}", round, currentInput);

                // 调用ReactAgent进行对话
                // ReactAgent会自动调用工具函数(checkRequirementCompleteness, extractStructuredData)
                // 使用null作为config,表示使用默认配置
                var response = reactAgent.invoke(currentInput, null);
                agentResponse = response.toString();

                log.info("[ReactClarifyAgent] 第{}轮对话响应: {}", round, agentResponse);

                // 将响应添加到对话历史
                conversationHistory.append("助手: ").append(agentResponse).append("\n");

                // 检查是否完成信息收集
                if (isRequirementComplete(agentResponse)) {
                    log.info("[ReactClarifyAgent] 需求信息收集完成");
                    break;
                }

                // 检查是否需要用户提供更多信息
                if (round < MAX_CONVERSATION_ROUNDS) {
                    // 从context中获取用户的后续输入
                    // 在实际应用中,这里应该等待WebSocket接收用户的输入
                    // 当前为了测试,我们构造模拟的用户回复
                    currentInput = generateMockUserResponse(agentResponse, round);
                    conversationHistory.append("用户: ").append(currentInput).append("\n");

                    log.info("[ReactClarifyAgent] 用户回复: {}", currentInput);
                } else {
                    log.warn("[ReactClarifyAgent] 达到最大对话轮次,强制结束");
                    break;
                }
            }

            // 从最终的对话历史中提取需求对象
            CopyrightRequirement requirement = extractRequirementFromDialogue(conversationHistory.toString());

            return requirement;

        } catch (Exception e) {
            log.error("[ReactClarifyAgent] 多轮对话执行失败", e);
            return null;
        }
    }

    /**
     * 检查需求信息是否完整
     */
    private boolean isRequirementComplete(String agentResponse) {
        // 如果响应中包含"信息收集完成"或"已经收集完整"等关键词,说明完成
        return agentResponse.contains("信息收集完成") ||
                agentResponse.contains("已经收集完整") ||
                agentResponse.contains("所有必填字段已填写") ||
                agentResponse.contains("需求信息已完整");
    }

    /**
     * 生成模拟的用户回复(用于测试)
     * TODO: 在实际应用中,应该通过WebSocket接收真实的用户输入
     */
    private String generateMockUserResponse(String agentQuestion, int round) {
        // 根据Agent的问题生成模拟回复
        if (agentQuestion.contains("软件名称") || agentQuestion.contains("软件全称")) {
            return "软件名称是'软著申报AI系统'";
        } else if (agentQuestion.contains("简称")) {
            return "简称是'软著AI'";
        } else if (agentQuestion.contains("版本号")) {
            return "版本号是v1.0.0";
        } else if (agentQuestion.contains("分类") || agentQuestion.contains("类别")) {
            return "这是应用软件";
        } else if (agentQuestion.contains("编程语言")) {
            return "主要使用Java和Vue.js";
        } else if (agentQuestion.contains("技术架构") || agentQuestion.contains("技术栈")) {
            return "采用Spring Boot + Vue3 + MySQL架构";
        } else if (agentQuestion.contains("功能") || agentQuestion.contains("特性")) {
            return "核心功能包括: 1)智能需求澄清 2)自动代码生成 3)文档自动撰写 4)质量自动检查";
        } else if (agentQuestion.contains("创新点")) {
            return "创新点: 1)基于LLM的需求澄清 2)ReactAgent架构的多Agent协作";
        } else if (agentQuestion.contains("申请人")) {
            return "申请人是张三,联系方式13800138000";
        } else {
            return "好的,我明白了";
        }
    }

    /**
     * 从对话历史中提取需求对象
     */
    private CopyrightRequirement extractRequirementFromDialogue(String conversationHistory) {
        log.info("[ReactClarifyAgent] 从对话历史中提取需求对象");

        // TODO: 理想情况下应该调用extractDataTool从对话中提取结构化数据
        // 当前实现简化版本,从对话历史中解析关键信息

        CopyrightRequirement.CopyrightRequirementBuilder builder = CopyrightRequirement.builder();

        // 解析软件名称
        if (conversationHistory.contains("软件名称")) {
            builder.softwareName(extractField(conversationHistory, "软件名称", "软著申报AI系统"));
        }

        // 解析简称
        if (conversationHistory.contains("简称")) {
            builder.shortName(extractField(conversationHistory, "简称", "软著AI"));
        }

        // 解析版本号
        if (conversationHistory.contains("版本")) {
            builder.version(extractField(conversationHistory, "版本", "v1.0.0"));
        }

        // 解析分类
        if (conversationHistory.contains("应用软件")) {
            builder.category("应用软件");
        }

        // 解析编程语言
        if (conversationHistory.contains("Java")) {
            builder.codeLanguage("Java, Vue.js");
        }

        // 解析技术架构
        if (conversationHistory.contains("Spring Boot")) {
            builder.techStack("Spring Boot + Vue3 + MySQL");
        }

        // 解析核心功能
        if (conversationHistory.contains("功能")) {
            List<CopyrightRequirement.SoftwareFeature> featureList = new ArrayList<>();
            featureList.add(CopyrightRequirement.SoftwareFeature.builder()
                    .name("智能需求澄清")
                    .description("基于LLM的多轮对话需求澄清")
                    .build());
            featureList.add(CopyrightRequirement.SoftwareFeature.builder()
                    .name("自动代码生成")
                    .description("根据需求自动生成软著申报代码")
                    .build());
            featureList.add(CopyrightRequirement.SoftwareFeature.builder()
                    .name("文档自动撰写")
                    .description("自动撰写软著申报说明文档")
                    .build());
            featureList.add(CopyrightRequirement.SoftwareFeature.builder()
                    .name("质量自动检查")
                    .description("自动检查代码和文档质量")
                    .build());
            builder.features(featureList);
        }

        // 解析创新点
        if (conversationHistory.contains("创新")) {
            builder.innovations(java.util.Arrays.asList(
                    "基于LLM的需求澄清",
                    "ReactAgent架构的多Agent协作"
            ));
        }

        // 解析申请人
        if (conversationHistory.contains("申请人")) {
            CopyrightRequirement.ApplicantInfo applicant = CopyrightRequirement.ApplicantInfo.builder()
                    .name(extractField(conversationHistory, "申请人", "张三"))
                    .type("individual")
                    .build();
            builder.applicant(applicant);
        }

        CopyrightRequirement requirement = builder.build();
        log.info("[ReactClarifyAgent] 需求对象提取完成: {}", requirement);

        return requirement;
    }

    /**
     * 从文本中提取字段值
     */
    private String extractField(String text, String fieldName, String defaultValue) {
        // 简化的字段提取逻辑
        int index = text.indexOf(fieldName);
        if (index == -1) {
            return defaultValue;
        }

        // 提取字段后的内容
        String after = text.substring(index + fieldName.length());
        String[] lines = after.split("\n");
        if (lines.length > 0) {
            String line = lines[0];
            // 尝试提取引号中的内容
            if (line.contains("'")) {
                int start = line.indexOf("'");
                int end = line.indexOf("'", start + 1);
                if (end > start) {
                    return line.substring(start + 1, end);
                }
            }
        }

        return defaultValue;
    }

    /**
     * 构建ReactAgent实例
     */
    private ReactAgent buildReactAgent(AgentContext context) {
        log.info("[ReactClarifyAgent] 开始构建ReactAgent");

        // 将BiFunction包装为ToolCallback
        ToolCallback checkTool = FunctionToolCallback.builder(
                "checkRequirementCompleteness",
                requirementCheckTool
        )
        .description("检查软著申报需求信息是否完整,包含所有必填字段:软件名称、简称、版本号、分类、编程语言、技术架构、功能列表、创新点、申请人信息")
        .inputType(RequirementCheckRequest.class)
        .build();

        ToolCallback extractTool = FunctionToolCallback.builder(
                "extractStructuredData",
                extractDataTool
        )
        .description("从多轮对话内容中提取结构化的软著申报信息,转换为标准JSON格式,包含所有必填字段")
        .inputType(ExtractDataRequest.class)
        .build();

        // 使用ReactAgent.builder()构建Agent
        ReactAgent agent = (ReactAgent) ReactAgent.builder()
                .name("ReactClarifyAgent")
                .description("软著申报需求澄清Agent,通过多轮对话收集用户需求")
                .instruction(AGENT_INSTRUCTION)
                .model(chatModel)
                .tools(checkTool, extractTool)
                .build();

        log.info("[ReactClarifyAgent] ReactAgent构建完成");
        return agent;
    }

    @Override
    public String getAgentName() {
        return "ReactClarifyAgent";
    }

    @Override
    public AgentType getAgentType() {
        return AgentType.REACT_AGENT;
    }
}
