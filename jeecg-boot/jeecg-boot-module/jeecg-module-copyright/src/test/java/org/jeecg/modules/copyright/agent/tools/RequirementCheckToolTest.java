package org.jeecg.modules.copyright.agent.tools;

import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.vo.RequirementCheckRequest;
import org.jeecg.modules.copyright.vo.RequirementCheckResponse;
import org.junit.jupiter.api.Test;

import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.*;

/**
 * RequirementCheckTool单元测试
 * 纯Java单元测试，不依赖Spring容器
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Slf4j
public class RequirementCheckToolTest {

    @Test
    public void testIncompleteRequirement() {
        log.info("==== 测试1: 不完整需求检查 ====");

        // 创建一个不完整的需求请求(只有3个字段)
        RequirementCheckRequest request = RequirementCheckRequest.builder()
                .softwareName("测试软件系统")
                .version("v1.0")
                .codeLanguage("Java")
                .build();

        // 调用工具函数
        RequirementCheckTool tool = new RequirementCheckTool();
        RequirementCheckResponse response = tool.apply(request, null);

        // 验证结果
        assertNotNull(response, "响应不应为null");
        assertFalse(response.isComplete(), "应该检测到信息不完整");
        assertEquals(33, response.getCompletenessPercentage(), "完整度应为33% (3/9)");
        assertEquals(6, response.getMissingFields().size(), "应该有6个缺失字段");
        assertNotNull(response.getNextFieldsToAsk(), "应该返回下一步询问字段");
        assertTrue(response.getNextFieldsToAsk().size() <= 2, "每次最多询问2个字段");

        log.info("✓ 完整度: {}%", response.getCompletenessPercentage());
        log.info("✓ 缺失字段: {}", response.getMissingFields());
        log.info("✓ 提示消息: {}", response.getMessage());
        log.info("✓ 下一步询问: {}", response.getNextFieldsToAsk());
    }

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

        RequirementCheckTool tool = new RequirementCheckTool();
        RequirementCheckResponse response = tool.apply(request, null);

        assertTrue(response.isComplete(), "所有字段都已填写,应该是完整的");
        assertEquals(100, response.getCompletenessPercentage(), "完整度应为100%");
        assertEquals(0, response.getMissingFields().size(), "不应有缺失字段");
        assertTrue(response.getMessage().contains("100%"), "提示消息应包含100%");

        log.info("✓ 提示消息: {}", response.getMessage());
    }

    @Test
    public void testFieldPriorityOrdering() {
        log.info("==== 测试3: 字段优先级排序 ====");

        // 创建只有低优先级字段的请求
        RequirementCheckRequest request = RequirementCheckRequest.builder()
                .shortName("系统简称")  // 最低优先级
                .build();

        RequirementCheckTool tool = new RequirementCheckTool();
        RequirementCheckResponse response = tool.apply(request, null);

        // 验证优先询问高优先级字段（softwareName应该在第一个）
        assertTrue(response.getNextFieldsToAsk().contains("softwareName"),
                "应该优先询问softwareName(最高优先级)");
        log.info("✓ 优先询问字段: {}", response.getNextFieldsToAsk());
    }

    @Test
    public void testChineseTranslation() {
        log.info("==== 测试4: 字段名称中文翻译 ====");

        RequirementCheckRequest request = RequirementCheckRequest.builder().build();

        RequirementCheckTool tool = new RequirementCheckTool();
        RequirementCheckResponse response = tool.apply(request, null);

        String message = response.getMessage();
        // 验证提示消息包含中文字段名
        assertTrue(message.contains("软件全称") ||
                        message.contains("版本号") ||
                        message.contains("编程语言"),
                "提示消息应包含中文字段名");
        log.info("✓ 提示消息: {}", message);
    }

    @Test
    public void testFeatureMinimumCount() {
        log.info("==== 测试5: 功能列表最少数量验证 ====");

        // features少于3个
        RequirementCheckRequest request1 = RequirementCheckRequest.builder()
                .features(Arrays.asList("功能1", "功能2"))  // 只有2个
                .build();

        RequirementCheckTool tool = new RequirementCheckTool();
        RequirementCheckResponse response1 = tool.apply(request1, null);

        assertTrue(response1.getMissingFields().contains("features"),
                "少于3个功能时,features应被视为缺失");

        // features等于3个
        RequirementCheckRequest request2 = RequirementCheckRequest.builder()
                .features(Arrays.asList("功能1", "功能2", "功能3"))  // 正好3个
                .build();

        RequirementCheckResponse response2 = tool.apply(request2, null);
        assertFalse(response2.getFieldCompleteness().get("features") == null ||
                        !response2.getFieldCompleteness().get("features"),
                "3个功能时,features应被视为已填写");

        log.info("✓ 功能列表数量验证通过");
    }

    @Test
    public void testInnovationMinimumCount() {
        log.info("==== 测试6: 创新点最少数量验证 ====");

        // innovations少于2个
        RequirementCheckRequest request1 = RequirementCheckRequest.builder()
                .innovations(Arrays.asList("创新点1"))  // 只有1个
                .build();

        RequirementCheckTool tool = new RequirementCheckTool();
        RequirementCheckResponse response1 = tool.apply(request1, null);

        assertTrue(response1.getMissingFields().contains("innovations"),
                "少于2个创新点时,innovations应被视为缺失");

        // innovations等于2个
        RequirementCheckRequest request2 = RequirementCheckRequest.builder()
                .innovations(Arrays.asList("创新点1", "创新点2"))  // 正好2个
                .build();

        RequirementCheckResponse response2 = tool.apply(request2, null);
        assertFalse(response2.getFieldCompleteness().get("innovations") == null ||
                        !response2.getFieldCompleteness().get("innovations"),
                "2个创新点时,innovations应被视为已填写");

        log.info("✓ 创新点数量验证通过");
    }
}
