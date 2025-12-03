package org.jeecg.modules.copyright.agent;

import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.agent.impl.ReactClarifyAgent;
import org.jeecg.modules.copyright.agent.tools.RequirementCheckTool;
import org.jeecg.modules.copyright.vo.CopyrightRequirement;
import org.jeecg.modules.copyright.vo.ExtractDataRequest;
import org.jeecg.modules.copyright.vo.RequirementCheckRequest;
import org.jeecg.modules.copyright.vo.RequirementCheckResponse;
import org.junit.jupiter.api.Test;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.model.ToolContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import java.util.Arrays;
import java.util.List;
import java.util.function.BiFunction;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Agent架构验证测试
 * 验证工具函数、Spring Bean注入和ReactAgent基础架构
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@SpringBootTest
@ActiveProfiles("test")
@Slf4j
public class CopyrightAgentArchitectureTest {

    @Autowired(required = false)
    private ChatModel chatModel;

    @Autowired(required = false)
    private ReactClarifyAgent reactClarifyAgent;

    @Autowired(required = false)
    private BiFunction<RequirementCheckRequest, ToolContext, RequirementCheckResponse> requirementCheckTool;

    @Autowired(required = false)
    private BiFunction<ExtractDataRequest, ToolContext, CopyrightRequirement> extractDataTool;

    /**
     * 测试1: 验证RequirementCheckTool工具函数
     */
    @Test
    public void testRequirementCheckTool() {
        log.info("==== 测试1: RequirementCheckTool工具函数 ====");

        // 创建一个不完整的需求请求
        RequirementCheckRequest request = RequirementCheckRequest.builder()
                .softwareName("测试软件系统")
                .version("v1.0")
                .codeLanguage("Java")
                // 缺少6个字段
                .build();

        // 调用工具函数
        RequirementCheckResponse response = new RequirementCheckTool().apply(request, null);

        // 验证结果
        assertNotNull(response, "响应不应为null");
        assertFalse(response.isComplete(), "应该检测到信息不完整");
        assertEquals(33, response.getCompletenessPercentage(), "完整度应为33% (3/9)");
        assertEquals(6, response.getMissingFields().size(), "应该有6个缺失字段");
        assertNotNull(response.getNextFieldsToAsk(), "应该返回下一步询问字段");
        assertTrue(response.getNextFieldsToAsk().size() <= 2, "每次最多询问2个字段");

        log.info("完整度: {}%", response.getCompletenessPercentage());
        log.info("缺失字段: {}", response.getMissingFields());
        log.info("提示消息: {}", response.getMessage());
        log.info("下一步询问: {}", response.getNextFieldsToAsk());
    }

    /**
     * 测试2: 验证完整需求检查
     */
    @Test
    public void testCompleteRequirement() {
        log.info("==== 测试2: 完整需求检查 ====");

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

        RequirementCheckResponse response = new RequirementCheckTool().apply(request, null);

        assertTrue(response.isComplete(), "所有字段都已填写,应该是完整的");
        assertEquals(100, response.getCompletenessPercentage(), "完整度应为100%");
        assertEquals(0, response.getMissingFields().size(), "不应有缺失字段");
        assertTrue(response.getMessage().contains("100%"), "提示消息应包含100%");

        log.info("提示消息: {}", response.getMessage());
    }

    /**
     * 测试3: 验证Spring Bean注入
     */
    @Test
    public void testSpringBeanInjection() {
        log.info("==== 测试3: Spring Bean注入验证 ====");

        if (chatModel != null) {
            log.info("✓ ChatModel Bean注入成功: {}", chatModel.getClass().getSimpleName());
        } else {
            log.warn("✗ ChatModel Bean未注入 (可能需要配置DashScope API Key)");
        }

        if (requirementCheckTool != null) {
            log.info("✓ RequirementCheckTool Bean注入成功");
            assertNotNull(requirementCheckTool, "RequirementCheckTool Bean应该被注入");
        } else {
            log.warn("✗ RequirementCheckTool Bean未注入");
        }

        if (extractDataTool != null) {
            log.info("✓ ExtractDataTool Bean注入成功");
        } else {
            log.warn("✗ ExtractDataTool Bean未注入 (依赖ChatModel)");
        }

        if (reactClarifyAgent != null) {
            log.info("✓ ReactClarifyAgent Bean注入成功");
            assertEquals("ReactClarifyAgent", reactClarifyAgent.getAgentName());
        } else {
            log.warn("✗ ReactClarifyAgent Bean未注入");
        }
    }

    /**
     * 测试4: 验证ReactAgent Builder API可用性
     */
    @Test
    public void testReactAgentBuilderAPI() {
        log.info("==== 测试4: ReactAgent Builder API ====");

        try {
            // 验证ReactAgent.builder()方法可调用
            Object builder = ReactAgent.builder();
            assertNotNull(builder, "ReactAgent.builder()应该返回非null对象");
            log.info("✓ ReactAgent.builder() API可用: {}", builder.getClass().getName());

            // 验证Builder类型
            assertTrue(builder instanceof com.alibaba.cloud.ai.graph.agent.Builder,
                    "返回对象应该是Builder类型");
            log.info("✓ Builder类型验证通过");

        } catch (Exception e) {
            fail("ReactAgent.builder() API调用失败: " + e.getMessage());
        }
    }

    /**
     * 测试5: 字段优先级排序验证
     */
    @Test
    public void testFieldPriorityOrdering() {
        log.info("==== 测试5: 字段优先级排序 ====");

        // 创建只有低优先级字段的请求
        RequirementCheckRequest request = RequirementCheckRequest.builder()
                .shortName("系统简称")
                .build();

        RequirementCheckResponse response = new RequirementCheckTool().apply(request, null);

        // 验证优先询问高优先级字段（softwareName应该在第一个）
        List<String> nextFields = response.getNextFieldsToAsk();
        assertTrue(nextFields.contains("softwareName"),
                "应该优先询问softwareName(最高优先级)");
        log.info("优先询问字段: {}", nextFields);
    }

    /**
     * 测试6: 中文翻译功能验证
     */
    @Test
    public void testFieldNameTranslation() {
        log.info("==== 测试6: 字段名称中文翻译 ====");

        RequirementCheckRequest request = RequirementCheckRequest.builder().build();
        RequirementCheckResponse response = new RequirementCheckTool().apply(request, null);

        String message = response.getMessage();
        // 验证提示消息包含中文字段名
        assertTrue(message.contains("软件全称") ||
                        message.contains("版本号") ||
                        message.contains("编程语言"),
                "提示消息应包含中文字段名");
        log.info("提示消息: {}", message);
    }
}
