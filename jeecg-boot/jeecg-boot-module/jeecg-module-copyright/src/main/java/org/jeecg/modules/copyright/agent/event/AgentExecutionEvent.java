package org.jeecg.modules.copyright.agent.event;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.jeecg.modules.copyright.agent.core.AgentResult;

import java.time.LocalDateTime;

/**
 * Agent执行事件
 * 用于Spring事件发布机制,实现Agent执行状态的实时推送
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AgentExecutionEvent {

    /**
     * 会话ID
     */
    private String sessionId;

    /**
     * Agent名称
     */
    private String agentName;

    /**
     * 执行状态
     */
    private AgentExecutionStatus status;

    /**
     * Agent执行结果(仅在COMPLETED或FAILED时有值)
     */
    private AgentResult result;

    /**
     * 事件发生时间
     */
    private LocalDateTime timestamp;

    /**
     * 执行时长(毫秒,仅在COMPLETED或FAILED时有值)
     */
    private Long durationMs;

    /**
     * 额外消息
     */
    private String message;

    /**
     * 创建Agent启动事件
     */
    public static AgentExecutionEvent started(String sessionId, String agentName) {
        return AgentExecutionEvent.builder()
                .sessionId(sessionId)
                .agentName(agentName)
                .status(AgentExecutionStatus.STARTED)
                .timestamp(LocalDateTime.now())
                .build();
    }

    /**
     * 创建Agent完成事件
     */
    public static AgentExecutionEvent completed(String sessionId, String agentName,
                                                AgentResult result, long durationMs) {
        return AgentExecutionEvent.builder()
                .sessionId(sessionId)
                .agentName(agentName)
                .status(AgentExecutionStatus.COMPLETED)
                .result(result)
                .durationMs(durationMs)
                .timestamp(LocalDateTime.now())
                .build();
    }

    /**
     * 创建Agent失败事件
     */
    public static AgentExecutionEvent failed(String sessionId, String agentName,
                                            AgentResult result, long durationMs) {
        return AgentExecutionEvent.builder()
                .sessionId(sessionId)
                .agentName(agentName)
                .status(AgentExecutionStatus.FAILED)
                .result(result)
                .durationMs(durationMs)
                .timestamp(LocalDateTime.now())
                .build();
    }
}
