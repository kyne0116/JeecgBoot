package org.jeecg.modules.copyright.agent.event;

import cn.hutool.json.JSONUtil;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.apply.service.ICopyrightSessionService;
import org.jeecg.modules.copyright.log.entity.CopyrightAgentLog;
import org.jeecg.modules.copyright.log.service.ICopyrightAgentLogService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * Agent事件监听器
 * 监听Agent执行事件,实现以下功能:
 * 1. 记录Agent执行日志到数据库
 * 2. 更新会话状态和进度
 * 3. 通过WebSocket推送实时状态到前端(TODO: 需要集成WebSocket)
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Component
@Slf4j
public class AgentEventListener {

    @Autowired
    private ICopyrightAgentLogService agentLogService;

    @Autowired
    private ICopyrightSessionService sessionService;

    // TODO: WebSocket推送器注入
    // @Autowired
    // private CopyrightChatWebSocket webSocketHandler;

    /**
     * 监听Agent执行事件
     * 使用@Async异步处理,避免阻塞Agent执行
     *
     * @param event Agent执行事件
     */
    @EventListener
    @Async
    public void handleAgentExecutionEvent(AgentExecutionEvent event) {
        try {
            log.debug("[Agent事件监听] 收到事件: session={}, agent={}, status={}",
                    event.getSessionId(), event.getAgentName(), event.getStatus());

            // 1. 记录Agent执行日志到数据库
            recordAgentLog(event);

            // 2. 更新会话进度JSON
            updateSessionProgress(event);

            // 3. 构建WebSocket消息推送到前端
            pushToWebSocket(event);

        } catch (Exception e) {
            log.error("[Agent事件监听] 处理Agent执行事件失败: session={}, agent={}",
                    event.getSessionId(), event.getAgentName(), e);
        }
    }

    /**
     * 记录Agent执行日志到数据库
     */
    private void recordAgentLog(AgentExecutionEvent event) {
        try {
            CopyrightAgentLog logEntity = new CopyrightAgentLog();
            logEntity.setSessionId(event.getSessionId());
            logEntity.setAgentName(event.getAgentName());

            // 将String状态码转换为Integer (STARTED=1, RUNNING=2, COMPLETED=3, FAILED=4)
            Integer statusCode = convertStatusToInteger(event.getStatus());
            logEntity.setStatus(statusCode);

            if (event.getStatus() == AgentExecutionStatus.STARTED) {
                // LocalDateTime转Date
                logEntity.setStartTime(java.sql.Timestamp.valueOf(event.getTimestamp()));
            } else if (event.getStatus() == AgentExecutionStatus.COMPLETED ||
                       event.getStatus() == AgentExecutionStatus.FAILED) {
                // LocalDateTime转Date
                logEntity.setEndTime(java.sql.Timestamp.valueOf(event.getTimestamp()));

                // Long转BigDecimal
                if (event.getDurationMs() != null) {
                    logEntity.setDurationMs(new java.math.BigDecimal(event.getDurationMs()));
                }

                if (event.getResult() != null) {
                    logEntity.setOutputResult(JSONUtil.toJsonStr(event.getResult()));
                    if (!event.getResult().isSuccess()) {
                        logEntity.setErrorMessage(event.getResult().getMessage());
                    }
                }
            }

            // LocalDateTime转Date
            logEntity.setCreateTime(java.sql.Timestamp.valueOf(LocalDateTime.now()));
            agentLogService.save(logEntity);

        } catch (Exception e) {
            log.error("[Agent日志] 记录Agent执行日志失败: session={}, agent={}",
                    event.getSessionId(), event.getAgentName(), e);
        }
    }

    /**
     * 将AgentExecutionStatus转换为Integer状态码
     */
    private Integer convertStatusToInteger(AgentExecutionStatus status) {
        switch (status) {
            case STARTED:
                return 1;
            case RUNNING:
                return 2;
            case COMPLETED:
                return 3;
            case FAILED:
                return 4;
            default:
                return 0;
        }
    }

    /**
     * 更新会话进度JSON
     */
    private void updateSessionProgress(AgentExecutionEvent event) {
        try {
            // TODO: 实现会话进度更新逻辑
            // 根据不同的Agent状态更新session表的progress_json字段
            log.debug("[会话进度] 更新会话进度: session={}, agent={}, status={}",
                    event.getSessionId(), event.getAgentName(), event.getStatus());

        } catch (Exception e) {
            log.error("[会话进度] 更新会话进度失败: session={}, agent={}",
                    event.getSessionId(), event.getAgentName(), e);
        }
    }

    /**
     * 推送Agent状态到WebSocket
     */
    private void pushToWebSocket(AgentExecutionEvent event) {
        try {
            // 构建WebSocket消息
            Map<String, Object> wsMessage = new HashMap<>();
            wsMessage.put("type", "agent_status");
            wsMessage.put("sessionId", event.getSessionId());
            wsMessage.put("agentName", event.getAgentName());
            wsMessage.put("status", event.getStatus().getCode());
            wsMessage.put("message", buildStatusMessage(event));
            wsMessage.put("timestamp", event.getTimestamp());

            if (event.getDurationMs() != null) {
                wsMessage.put("durationMs", event.getDurationMs());
            }

            // TODO: 通过WebSocket推送消息到前端
            // webSocketHandler.sendMessageToSession(event.getSessionId(), wsMessage);
            log.debug("[WebSocket推送] Agent状态推送: {}", JSONUtil.toJsonStr(wsMessage));

        } catch (Exception e) {
            log.error("[WebSocket推送] 推送Agent状态失败: session={}, agent={}",
                    event.getSessionId(), event.getAgentName(), e);
        }
    }

    /**
     * 构建状态消息
     */
    private String buildStatusMessage(AgentExecutionEvent event) {
        String agentName = event.getAgentName();
        AgentExecutionStatus status = event.getStatus();

        switch (status) {
            case STARTED:
                return getAgentStartMessage(agentName);
            case COMPLETED:
                return getAgentCompleteMessage(agentName);
            case FAILED:
                return getAgentFailMessage(agentName, event.getResult());
            default:
                return "Agent状态更新: " + agentName;
        }
    }

    /**
     * 获取Agent启动消息
     */
    private String getAgentStartMessage(String agentName) {
        switch (agentName) {
            case "ReactClarifyAgent":
                return "正在与您对话,收集软著申报信息...";
            case "ReactCodeGenAgent":
                return "正在生成源代码(5000-6000行)...";
            case "ReactFormFillAgent":
                return "正在填写《软著信息采集表》...";
            case "ReactDocWriterAgent":
                return "正在撰写《软著申报说明文档》...";
            case "ReactQualityCheckAgent":
                return "正在进行质量检查...";
            default:
                return "Agent " + agentName + " 开始执行";
        }
    }

    /**
     * 获取Agent完成消息
     */
    private String getAgentCompleteMessage(String agentName) {
        switch (agentName) {
            case "ReactClarifyAgent":
                return "需求信息收集完成!";
            case "ReactCodeGenAgent":
                return "源代码生成完成!";
            case "ReactFormFillAgent":
                return "信息采集表填写完成!";
            case "ReactDocWriterAgent":
                return "申报说明文档撰写完成!";
            case "ReactQualityCheckAgent":
                return "质量检查完成!";
            default:
                return "Agent " + agentName + " 执行完成";
        }
    }

    /**
     * 获取Agent失败消息
     */
    private String getAgentFailMessage(String agentName, org.jeecg.modules.copyright.agent.core.AgentResult result) {
        String message = result != null ? result.getMessage() : "执行失败";
        return agentName + " 执行失败: " + message;
    }
}
