package org.jeecg.modules.copyright.agent.impl;

import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.agent.core.AgentContext;
import org.jeecg.modules.copyright.agent.core.AgentResult;
import org.jeecg.modules.copyright.vo.CopyrightRequirement;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * ReactClarifyAgent集成测试
 *
 * 运行前提条件:
 * 1. 配置环境变量: AI_API_KEY, AI_BASE_URL, AI_MODEL
 * 2. 确保能连接到LLM服务
 *
 * 运行方式:
 * - IDE: 右键运行此测试类
 * - 命令行: mvn test -Dtest=ReactClarifyAgentIntegrationTest
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@SpringBootTest
@ActiveProfiles("dev")
@Slf4j
public class ReactClarifyAgentIntegrationTest {

    @Autowired
    private ReactClarifyAgent reactClarifyAgent;

    private AgentContext context;

    @BeforeEach
    public void setUp() {
        // 准备测试上下文
        Map<String, Object> params = new HashMap<>();
        params.put("userInput", "我想申报一个软著,软件名称叫'智能办公助手',是一个应用软件");

        context = AgentContext.builder()
                .sessionId("test_session_001")
                .userId("test_user")
                .params(params)
                .build();
    }

    @Test
    public void testExecuteWithMockDialogue() {
        log.info("========== 开始测试ReactClarifyAgent ==========");

        // 执行Agent
        AgentResult result = reactClarifyAgent.execute(context);

        // 验证结果
        assertNotNull(result, "AgentResult不应为null");
        assertTrue(result.isSuccess(), "执行应该成功");
        assertNotNull(result.getData(), "结果数据不应为null");

        // 验证返回的数据类型
        Object data = result.getData();
        assertTrue(data instanceof CopyrightRequirement, "返回数据应该是CopyrightRequirement类型");

        CopyrightRequirement requirement = (CopyrightRequirement) data;

        // 验证关键字段
        assertNotNull(requirement.getSoftwareName(), "软件名称不应为null");
        assertNotNull(requirement.getVersion(), "版本号不应为null");

        log.info("软件名称: {}", requirement.getSoftwareName());
        log.info("版本号: {}", requirement.getVersion());
        log.info("分类: {}", requirement.getCategory());
        log.info("编程语言: {}", requirement.getCodeLanguage());
        log.info("技术栈: {}", requirement.getTechStack());

        if (requirement.getFeatures() != null && !requirement.getFeatures().isEmpty()) {
            log.info("核心功能数量: {}", requirement.getFeatures().size());
            requirement.getFeatures().forEach(feature ->
                log.info("  - {}: {}", feature.getName(), feature.getDescription())
            );
        }

        if (requirement.getInnovations() != null && !requirement.getInnovations().isEmpty()) {
            log.info("创新点数量: {}", requirement.getInnovations().size());
            requirement.getInnovations().forEach(innovation ->
                log.info("  - {}", innovation)
            );
        }

        if (requirement.getApplicant() != null) {
            log.info("申请人: {} ({})",
                requirement.getApplicant().getName(),
                requirement.getApplicant().getType()
            );
        }

        log.info("========== ReactClarifyAgent测试完成 ==========");
    }

    @Test
    public void testAgentName() {
        assertEquals("ReactClarifyAgent", reactClarifyAgent.getAgentName());
    }

    /**
     * 验证环境配置是否正确
     * 这个测试会检查是否配置了必要的环境变量
     */
    @Test
    public void testEnvironmentConfiguration() {
        String apiKey = System.getenv("AI_API_KEY");
        String baseUrl = System.getenv("AI_BASE_URL");
        String model = System.getenv("AI_MODEL");

        log.info("API Key配置: {}", apiKey != null ? "已配置" : "未配置");
        log.info("Base URL: {}", baseUrl != null ? baseUrl : "未配置(将使用默认值)");
        log.info("Model: {}", model != null ? model : "未配置(将使用默认值)");

        if (apiKey == null || apiKey.equals("sk-your-key-here")) {
            log.warn("⚠️  环境变量AI_API_KEY未正确配置,LLM调用可能失败");
            log.warn("   请设置环境变量或在.env文件中配置");
            log.warn("   export AI_API_KEY=your-actual-api-key");
        }
    }
}
