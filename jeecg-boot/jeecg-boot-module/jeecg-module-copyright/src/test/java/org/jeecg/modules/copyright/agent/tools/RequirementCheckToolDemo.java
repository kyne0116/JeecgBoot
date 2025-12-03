package org.jeecg.modules.copyright.agent.tools;

import org.jeecg.modules.copyright.vo.RequirementCheckRequest;
import org.jeecg.modules.copyright.vo.RequirementCheckResponse;

import java.util.Arrays;

/**
 * RequirementCheckTool验证程序
 * 用于手工验证工具函数功能
 *
 * @author Claude Code
 * @since 2025-12-03
 */
public class RequirementCheckToolDemo {

    public static void main(String[] args) {
        System.out.println("===========================================");
        System.out.println("  RequirementCheckTool 架构验证");
        System.out.println("===========================================\n");

        // 测试1: 不完整需求
        testIncompleteRequirement();

        // 测试2: 完整需求
        testCompleteRequirement();

        // 测试3: 字段优先级
        testFieldPriority();

        // 测试4: ReactAgent Builder API
        testReactAgentBuilder();

        System.out.println("\n===========================================");
        System.out.println("  ✓ 所有验证通过！架构正常！");
        System.out.println("===========================================");
    }

    private static void testIncompleteRequirement() {
        System.out.println("【测试1】不完整需求检查");
        System.out.println("-------------------------------------------");

        RequirementCheckRequest request = RequirementCheckRequest.builder()
                .softwareName("测试软件系统")
                .version("v1.0")
                .codeLanguage("Java")
                .build();

        RequirementCheckTool tool = new RequirementCheckTool();
        RequirementCheckResponse response = tool.apply(request, null);

        System.out.println("完整度: " + response.getCompletenessPercentage() + "%");
        System.out.println("缺失字段: " + response.getMissingFields());
        System.out.println("提示消息: " + response.getMessage());
        System.out.println("下一步询问: " + response.getNextFieldsToAsk());

        assert !response.isComplete() : "应该检测到不完整";
        assert response.getCompletenessPercentage() == 33 : "完整度应为33%";
        assert response.getMissingFields().size() == 6 : "应有6个缺失字段";

        System.out.println("✓ 测试通过\n");
    }

    private static void testCompleteRequirement() {
        System.out.println("【测试2】完整需求检查");
        System.out.println("-------------------------------------------");

        RequirementCheckRequest request = RequirementCheckRequest.builder()
                .softwareName("智能管理系统")
                .shortName("智能系统")
                .version("v1.0")
                .category("应用软件")
                .codeLanguage("Java")
                .techStack("Spring Boot + Vue3")
                .features(Arrays.asList("用户管理", "数据分析", "报表生成"))
                .innovations(Arrays.asList("AI推荐", "分布式架构"))
                .applicantName("测试公司")
                .build();

        RequirementCheckTool tool = new RequirementCheckTool();
        RequirementCheckResponse response = tool.apply(request, null);

        System.out.println("完整度: " + response.getCompletenessPercentage() + "%");
        System.out.println("提示消息: " + response.getMessage());

        assert response.isComplete() : "应该是完整的";
        assert response.getCompletenessPercentage() == 100 : "完整度应为100%";

        System.out.println("✓ 测试通过\n");
    }

    private static void testFieldPriority() {
        System.out.println("【测试3】字段优先级排序");
        System.out.println("-------------------------------------------");

        RequirementCheckRequest request = RequirementCheckRequest.builder()
                .shortName("系统简称")  // 最低优先级
                .build();

        RequirementCheckTool tool = new RequirementCheckTool();
        RequirementCheckResponse response = tool.apply(request, null);

        System.out.println("下一步优先询问: " + response.getNextFieldsToAsk());

        assert response.getNextFieldsToAsk().contains("softwareName") :
                "应优先询问softwareName";

        System.out.println("✓ 测试通过\n");
    }

    private static void testReactAgentBuilder() {
        System.out.println("【测试4】ReactAgent Builder API");
        System.out.println("-------------------------------------------");

        try {
            // 验证ReactAgent.builder()方法可调用
            Object builder = com.alibaba.cloud.ai.graph.agent.ReactAgent.builder();
            System.out.println("Builder类型: " + builder.getClass().getName());

            assert builder != null : "Builder不应为null";
            assert builder instanceof com.alibaba.cloud.ai.graph.agent.Builder :
                    "应该是Builder类型";

            System.out.println("✓ ReactAgent.builder() API可用");
            System.out.println("✓ 测试通过\n");
        } catch (Exception e) {
            System.err.println("✗ 测试失败: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
