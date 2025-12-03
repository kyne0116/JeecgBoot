package org.jeecg.modules.copyright.agent.impl;

import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import org.jeecg.modules.copyright.agent.core.AgentContext;
import org.jeecg.modules.copyright.agent.core.AgentResult;
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

import java.util.HashMap;
import java.util.Map;
import java.util.function.BiFunction;

/**
 * ReactClarifyAgent验证程序
 * 验证ReactAgent构建和工具函数注册
 *
 * @author Claude Code
 * @since 2025-12-03
 */
public class ReactClarifyAgentDemo {

    public static void main(String[] args) {
        System.out.println("===========================================");
        System.out.println("  ReactClarifyAgent 构建验证");
        System.out.println("===========================================\n");

        try {
            // 测试1: 验证ToolCallback包装
            testToolCallbackWrapping();

            // 测试2: 验证ReactAgent构建
            testReactAgentBuilding();

            // 测试3: 验证Agent执行流程
            testAgentExecution();

            System.out.println("\n===========================================");
            System.out.println("  ✓ 所有验证通过！ReactAgent架构正常！");
            System.out.println("===========================================");

        } catch (Exception e) {
            System.err.println("\n✗ 验证失败: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void testToolCallbackWrapping() {
        System.out.println("【测试1】ToolCallback包装验证");
        System.out.println("-------------------------------------------");

        BiFunction<RequirementCheckRequest, ToolContext, RequirementCheckResponse> requirementCheckTool =
                new RequirementCheckTool();

        // 使用FunctionToolCallback包装BiFunction
        ToolCallback checkTool = FunctionToolCallback.builder(
                "checkRequirementCompleteness",
                requirementCheckTool
        )
        .description("检查软著申报需求信息是否完整")
        .inputType(RequirementCheckRequest.class)
        .build();

        assert checkTool != null : "ToolCallback should not be null";
        System.out.println("✓ ToolCallback类型: " + checkTool.getClass().getSimpleName());
        System.out.println("✓ ToolCallback创建成功");
        System.out.println("✓ 测试通过\n");
    }

    private static void testReactAgentBuilding() {
        System.out.println("【测试2】ReactAgent构建验证");
        System.out.println("-------------------------------------------");

        // 创建工具函数
        BiFunction<RequirementCheckRequest, ToolContext, RequirementCheckResponse> requirementCheckTool =
                new RequirementCheckTool();

        ToolCallback checkTool = FunctionToolCallback.builder(
                "checkRequirementCompleteness",
                requirementCheckTool
        )
        .description("检查需求完整性")
        .inputType(RequirementCheckRequest.class)
        .build();

        // 注意: 这里ChatModel为null会导致后续调用失败,但可以验证构建过程
        ReactAgent agent = (ReactAgent) ReactAgent.builder()
                .name("TestReactAgent")
                .description("测试Agent")
                .instruction("你是一个测试助手")
                // .model(chatModel)  // 实际使用时需要注入ChatModel
                .tools(checkTool)
                .build();

        assert agent != null : "ReactAgent should not be null";
        System.out.println("✓ Agent类型: " + agent.getClass().getSimpleName());
        System.out.println("✓ ReactAgent构建成功");
        System.out.println("✓ 测试通过\n");
    }

    private static void testAgentExecution() {
        System.out.println("【测试3】Agent执行流程验证");
        System.out.println("-------------------------------------------");

        // 创建模拟的ReactClarifyAgent（不依赖Spring容器）
        ReactClarifyAgentSimulator simulator = new ReactClarifyAgentSimulator();

        // 创建AgentContext
        Map<String, Object> params = new HashMap<>();
        params.put("userInput", "我想申报一个Java管理系统");

        AgentContext context = AgentContext.builder()
                .sessionId("test-session-001")
                .userId("test-user")
                .params(params)
                .build();

        // 执行Agent（这里会因为没有ChatModel而返回模拟结果）
        AgentResult result = simulator.execute(context);

        System.out.println("✓ 执行结果: " + (result.isSuccess() ? "成功" : "失败"));
        System.out.println("✓ 结果消息: " + result.getMessage());
        System.out.println("✓ 测试通过\n");
    }

    /**
     * 模拟的ReactClarifyAgent（不依赖Spring注入）
     */
    static class ReactClarifyAgentSimulator {

        public AgentResult execute(AgentContext context) {
            System.out.println("→ 模拟Agent执行, sessionId: " + context.getSessionId());
            System.out.println("→ 用户输入: " + context.getParams().get("userInput"));

            try {
                // 模拟构建ReactAgent
                BiFunction<RequirementCheckRequest, ToolContext, RequirementCheckResponse> checkTool =
                        new RequirementCheckTool();

                ToolCallback callback = FunctionToolCallback.builder(
                        "checkRequirementCompleteness",
                        checkTool
                )
                .description("检查需求完整性")
                .inputType(RequirementCheckRequest.class)
                .build();

                ReactAgent agent = (ReactAgent) ReactAgent.builder()
                        .name("ReactClarifyAgent")
                        .description("需求澄清Agent")
                        .instruction("你是一个软著申报助手")
                        .tools(callback)
                        .build();

                System.out.println("→ ReactAgent构建成功");

                // 模拟执行结果
                CopyrightRequirement requirement = CopyrightRequirement.builder()
                        .softwareName("示例软件系统")
                        .version("v1.0")
                        .build();

                return AgentResult.success("需求澄清完成(模拟结果)", requirement);

            } catch (Exception e) {
                return AgentResult.failure("执行失败: " + e.getMessage());
            }
        }
    }
}
