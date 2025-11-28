package org.jeecg.modules.ai.config;

import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import com.alibaba.cloud.ai.graph.exception.GraphStateException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.boot.autoconfigure.condition.ConditionalOnBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 聊天Agent配置
 * 创建一个简单的聊天对话Agent
 *
 * @author JeecgBoot
 * @since 2025-11-28
 */
@Slf4j
@Configuration
public class ChatAgentConfig {

    private static final String INSTRUCTION = """
            你是一个友好、专业的AI助手，擅长回答用户的各种问题。
            请用简洁、清晰的语言回答用户的提问。
            在回答时保持礼貌和耐心，如果不确定答案，请如实告知。
            """;

    /**
     * 创建聊天Agent
     * 使用ReactAgent实现简单的对话功能
     *
     * @param chatModel Spring AI的ChatModel
     * @return ReactAgent实例
     */
    @Bean
    public ReactAgent chatAgent(ChatModel chatModel) throws GraphStateException {
        log.info("Creating ChatAgent with ReactAgent framework");
        // 使用Builder模式创建ReactAgent
        ReactAgent agent = ReactAgent.builder()
                .name("chat-agent")
                .description("简单的聊天对话Agent，可以进行日常对话交流")
                .model(chatModel)
                .instruction(INSTRUCTION)
                .enableLogging(true)
                .build();

        log.info("ChatAgent created successfully: {}", agent.name());
        return agent;
    }
}
