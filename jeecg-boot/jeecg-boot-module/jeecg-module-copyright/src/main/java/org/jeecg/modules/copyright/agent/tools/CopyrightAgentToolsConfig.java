package org.jeecg.modules.copyright.agent.tools;

import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.vo.RequirementCheckRequest;
import org.jeecg.modules.copyright.vo.RequirementCheckResponse;
import org.springframework.ai.chat.model.ToolContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.function.BiFunction;

/**
 * 软著申报Agent工具函数配置类
 * 定义ReactClarifyAgent使用的工具函数
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Configuration
@Slf4j
public class CopyrightAgentToolsConfig {

    /**
     * 需求完整性检查工具
     * 检查用户提供的软著申报信息是否完整(9个必填字段)
     */
    @Bean
    public BiFunction<RequirementCheckRequest, ToolContext, RequirementCheckResponse> requirementCheckTool() {
        log.info("[Agent配置] 创建RequirementCheckTool bean");
        return new RequirementCheckTool();
    }

    // ExtractDataTool 通过 @Component 自动注册为Bean
    // ReactClarifyAgent 可以直接 @Autowired 注入 ExtractDataTool 组件
}
