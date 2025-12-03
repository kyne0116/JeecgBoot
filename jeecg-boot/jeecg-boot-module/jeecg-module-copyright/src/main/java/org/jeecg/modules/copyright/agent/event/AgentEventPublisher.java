package org.jeecg.modules.copyright.agent.event;

import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.agent.core.AgentResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Component;

/**
 * Agent事件发布器
 * 负责发布Agent执行的各种事件,供AgentEventListener监听
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Component
@Slf4j
public class AgentEventPublisher {

    @Autowired
    private ApplicationEventPublisher eventPublisher;

    /**
     * 发布Agent启动事件
     *
     * @param sessionId 会话ID
     * @param agentName Agent名称
     */
    public void publishAgentStarted(String sessionId, String agentName) {
        try {
            AgentExecutionEvent event = AgentExecutionEvent.started(sessionId, agentName);
            eventPublisher.publishEvent(event);
            log.info("[Agent事件] Agent启动: session={}, agent={}", sessionId, agentName);
        } catch (Exception e) {
            log.error("[Agent事件] 发布Agent启动事件失败: session={}, agent={}",
                    sessionId, agentName, e);
        }
    }

    /**
     * 发布Agent完成事件
     *
     * @param sessionId  会话ID
     * @param agentName  Agent名称
     * @param result     Agent执行结果
     * @param durationMs 执行时长(毫秒)
     */
    public void publishAgentCompleted(String sessionId, String agentName,
                                      AgentResult result, long durationMs) {
        try {
            AgentExecutionEvent event = AgentExecutionEvent.completed(
                    sessionId, agentName, result, durationMs);
            eventPublisher.publishEvent(event);
            log.info("[Agent事件] Agent完成: session={}, agent={}, duration={}ms, success={}",
                    sessionId, agentName, durationMs, result.isSuccess());
        } catch (Exception e) {
            log.error("[Agent事件] 发布Agent完成事件失败: session={}, agent={}",
                    sessionId, agentName, e);
        }
    }

    /**
     * 发布Agent失败事件
     *
     * @param sessionId  会话ID
     * @param agentName  Agent名称
     * @param result     Agent执行结果
     * @param durationMs 执行时长(毫秒)
     */
    public void publishAgentFailed(String sessionId, String agentName,
                                   AgentResult result, long durationMs) {
        try {
            AgentExecutionEvent event = AgentExecutionEvent.failed(
                    sessionId, agentName, result, durationMs);
            eventPublisher.publishEvent(event);
            log.error("[Agent事件] Agent失败: session={}, agent={}, duration={}ms, error={}",
                    sessionId, agentName, durationMs, result.getMessage());
        } catch (Exception e) {
            log.error("[Agent事件] 发布Agent失败事件失败: session={}, agent={}",
                    sessionId, agentName, e);
        }
    }

    /**
     * 发布自定义消息事件
     *
     * @param sessionId 会话ID
     * @param agentName Agent名称
     * @param message   自定义消息
     */
    public void publishCustomMessage(String sessionId, String agentName, String message) {
        try {
            AgentExecutionEvent event = AgentExecutionEvent.builder()
                    .sessionId(sessionId)
                    .agentName(agentName)
                    .status(AgentExecutionStatus.RUNNING)
                    .message(message)
                    .timestamp(java.time.LocalDateTime.now())
                    .build();
            eventPublisher.publishEvent(event);
            log.debug("[Agent事件] 自定义消息: session={}, agent={}, message={}",
                    sessionId, agentName, message);
        } catch (Exception e) {
            log.error("[Agent事件] 发布自定义消息事件失败: session={}, agent={}",
                    sessionId, agentName, e);
        }
    }
}
