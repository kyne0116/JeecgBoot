package org.jeecg.modules.copyright.agent.service;

import lombok.extern.slf4j.Slf4j;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.jeecg.modules.copyright.agent.core.AgentContext;
import org.jeecg.modules.copyright.agent.core.AgentResult;
import org.jeecg.modules.copyright.agent.impl.ReactClarifyAgent;
import org.jeecg.modules.copyright.apply.service.ICopyrightMessageService;
import org.jeecg.modules.copyright.apply.service.ICopyrightSessionService;
import org.jeecg.modules.copyright.sse.manager.SseEmitterManager;
import org.jeecg.modules.copyright.vo.CopyrightRequirement;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.*;

/**
 * ReactClarifyAgent SSE集成服务
 *
 * 核心职责：
 * 1. 协调ReactClarifyAgent、SSE推送、数据库持久化三者
 * 2. 管理用户输入队列，实现真实用户输入等待机制
 * 3. 拦截Agent响应，实现流式推送
 * 4. 自动持久化对话历史
 * 5. 管理会话状态
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Service
@Slf4j
public class ReactClarifyAgentSSEService {

    @Autowired
    private ReactClarifyAgent reactClarifyAgent;

    @Autowired
    private SseEmitterManager emitterManager;

    @Autowired
    private ICopyrightMessageService messageService;

    @Autowired
    private ICopyrightSessionService sessionService;

    @Autowired
    private ObjectMapper objectMapper;

    /**
     * 用户输入队列
     * key: sessionId, value: 阻塞队列（用于等待用户输入）
     */
    private final Map<String, BlockingQueue<String>> userInputQueues = new ConcurrentHashMap<>();

    /**
     * 会话状态
     * key: sessionId, value: 会话元数据
     */
    private final Map<String, SessionMetadata> sessionMetadataMap = new ConcurrentHashMap<>();

    /**
     * 启动需求澄清流程（异步）
     *
     * @param sessionId 会话ID
     * @param username  用户名
     * @param initialMessage 用户初始消息
     */
    @Async
    public void startClarification(String sessionId, String username, String initialMessage) {
        log.info("[ReactClarifyAgentSSEService] 启动需求澄清流程, sessionId: {}, user: {}",
                sessionId, username);

        try {
            // 1. 初始化会话元数据
            SessionMetadata metadata = new SessionMetadata(sessionId, username);
            sessionMetadataMap.put(sessionId, metadata);

            // 2. 创建用户输入队列
            BlockingQueue<String> inputQueue = new LinkedBlockingQueue<>();
            userInputQueues.put(sessionId, inputQueue);

            // 3. 推送状态：开始需求澄清
            emitterManager.sendStatus(sessionId, "正在启动需求澄清流程...");

            // 4. 保存用户初始消息
            messageService.saveMessage(sessionId, "user", initialMessage, "ReactClarifyAgent");

            // 5. 构建AgentContext
            AgentContext context = AgentContext.builder()
                    .sessionId(sessionId)
                    .userId(username)
                    .params(Map.of("userInput", initialMessage))
                    .build();

            // 6. 注入回调接口到context，供Agent调用
            context.getParams().put("inputCallback", (UserInputCallback) this::waitForUserInput);
            context.getParams().put("outputCallback", (AgentOutputCallback) this::onAgentOutput);

            // 7. 执行ReactClarifyAgent
            AgentResult result = reactClarifyAgent.execute(context);

            // 8. 处理执行结果
            if (result.isSuccess()) {
                log.info("[ReactClarifyAgentSSEService] 需求澄清完成, sessionId: {}", sessionId);

                // 提取需求对象
                CopyrightRequirement requirement = (CopyrightRequirement) result.getData();

                // 将需求对象转换为JSON字符串
                String requirementJson = objectMapper.writeValueAsString(requirement);

                // 更新会话状态和需求JSON
                sessionService.updateSessionStatus(sessionId, "GENERATING");
                sessionService.updateRequirement(sessionId, requirementJson);

                // 推送完成状态
                emitterManager.sendStatus(sessionId, "需求澄清完成！开始生成软著材料...");

                // TODO: 触发后续的生成流程 (T010-T014 Agents)

            } else {
                log.error("[ReactClarifyAgentSSEService] 需求澄清失败, sessionId: {}, reason: {}",
                        sessionId, result.getMessage());

                // 更新会话状态为失败
                sessionService.updateSessionStatus(sessionId, "FAILED");

                // 推送错误消息
                emitterManager.sendError(sessionId, "需求澄清失败: " + result.getMessage());
            }

        } catch (Exception e) {
            log.error("[ReactClarifyAgentSSEService] 需求澄清流程异常, sessionId: " + sessionId, e);

            // 更新会话状态
            sessionService.updateSessionStatus(sessionId, "FAILED");

            // 推送错误消息
            emitterManager.sendError(sessionId, "系统异常: " + e.getMessage());

        } finally {
            // 清理资源
            cleanup(sessionId);
        }
    }

    /**
     * 提交用户输入
     *
     * 当用户通过HTTP POST发送消息时调用，将消息放入队列
     *
     * @param sessionId 会话ID
     * @param userInput 用户输入
     * @return 是否提交成功
     */
    public boolean submitUserInput(String sessionId, String userInput) {
        log.info("[ReactClarifyAgentSSEService] 提交用户输入, sessionId: {}, input: {}",
                sessionId, userInput);

        BlockingQueue<String> queue = userInputQueues.get(sessionId);
        if (queue == null) {
            log.warn("[ReactClarifyAgentSSEService] 会话不存在或已结束, sessionId: {}", sessionId);
            return false;
        }

        try {
            // 1. 保存用户消息到数据库
            messageService.saveMessage(sessionId, "user", userInput, "ReactClarifyAgent");

            // 2. 放入队列，唤醒等待的Agent
            queue.offer(userInput, 5, TimeUnit.SECONDS);

            log.info("[ReactClarifyAgentSSEService] 用户输入已放入队列, sessionId: {}", sessionId);
            return true;

        } catch (InterruptedException e) {
            log.error("[ReactClarifyAgentSSEService] 提交用户输入超时, sessionId: " + sessionId, e);
            Thread.currentThread().interrupt();
            return false;
        }
    }

    /**
     * 等待用户输入（供ReactClarifyAgent调用）
     *
     * 这是替代generateMockUserResponse()的真实用户输入机制
     *
     * @param sessionId 会话ID
     * @param agentQuestion Agent的提问
     * @return 用户输入
     * @throws InterruptedException 等待被中断
     * @throws TimeoutException 等待超时
     */
    private String waitForUserInput(String sessionId, String agentQuestion)
            throws InterruptedException, TimeoutException {

        log.info("[ReactClarifyAgentSSEService] Agent等待用户输入, sessionId: {}", sessionId);

        BlockingQueue<String> queue = userInputQueues.get(sessionId);
        if (queue == null) {
            throw new IllegalStateException("会话队列不存在: " + sessionId);
        }

        // 等待用户输入，最多等待5分钟
        String userInput = queue.poll(5, TimeUnit.MINUTES);

        if (userInput == null) {
            log.warn("[ReactClarifyAgentSSEService] 等待用户输入超时, sessionId: {}", sessionId);
            throw new TimeoutException("等待用户输入超时(5分钟)");
        }

        log.info("[ReactClarifyAgentSSEService] 收到用户输入, sessionId: {}, input: {}",
                sessionId, userInput);

        return userInput;
    }

    /**
     * Agent输出回调（供ReactClarifyAgent调用）
     *
     * 拦截Agent的输出，进行SSE推送和数据库持久化
     *
     * @param sessionId 会话ID
     * @param agentResponse Agent响应
     */
    private void onAgentOutput(String sessionId, String agentResponse) {
        log.debug("[ReactClarifyAgentSSEService] Agent输出, sessionId: {}, response: {}",
                sessionId, agentResponse);

        try {
            // 1. 通过SSE推送Agent响应
            // 模拟流式推送效果（逐字推送）
            pushStreamingText(sessionId, agentResponse);

            // 2. 保存Agent响应到数据库
            messageService.saveMessage(sessionId, "assistant", agentResponse, "ReactClarifyAgent");

            log.debug("[ReactClarifyAgentSSEService] Agent输出已推送和保存, sessionId: {}", sessionId);

        } catch (Exception e) {
            log.error("[ReactClarifyAgentSSEService] 处理Agent输出失败, sessionId: " + sessionId, e);
        }
    }

    /**
     * 流式推送文本（模拟逐字显示）
     *
     * @param sessionId 会话ID
     * @param text 完整文本
     */
    private void pushStreamingText(String sessionId, String text) {
        // 推送状态：正在回复
        emitterManager.sendStatus(sessionId, "正在回复...");

        // 将文本按字符分割，模拟流式效果
        // 实际应用中可以使用ChatModel.stream()的真实流式响应
        char[] chars = text.toCharArray();
        StringBuilder buffer = new StringBuilder();

        for (int i = 0; i < chars.length; i++) {
            buffer.append(chars[i]);

            // 每5个字符推送一次，或者遇到标点符号
            if (i % 5 == 0 || isPunctuation(chars[i]) || i == chars.length - 1) {
                emitterManager.sendChat(sessionId, buffer.toString());
                buffer = new StringBuilder();

                // 模拟打字延迟
                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }

        // 推送完成状态
        emitterManager.sendStatus(sessionId, "回复完成");
    }

    /**
     * 判断是否为标点符号
     */
    private boolean isPunctuation(char c) {
        return c == '，' || c == '。' || c == '！' || c == '？' || c == '、' ||
               c == ',' || c == '.' || c == '!' || c == '?' || c == ';';
    }

    /**
     * 检查会话是否活跃
     *
     * @param sessionId 会话ID
     * @return 是否活跃
     */
    public boolean isSessionActive(String sessionId) {
        return sessionMetadataMap.containsKey(sessionId);
    }

    /**
     * 清理会话资源
     *
     * @param sessionId 会话ID
     */
    private void cleanup(String sessionId) {
        log.info("[ReactClarifyAgentSSEService] 清理会话资源, sessionId: {}", sessionId);

        userInputQueues.remove(sessionId);
        sessionMetadataMap.remove(sessionId);
    }

    /**
     * 用户输入回调接口
     */
    @FunctionalInterface
    public interface UserInputCallback {
        String waitForInput(String sessionId, String agentQuestion)
                throws InterruptedException, TimeoutException;
    }

    /**
     * Agent输出回调接口
     */
    @FunctionalInterface
    public interface AgentOutputCallback {
        void onOutput(String sessionId, String agentResponse);
    }

    /**
     * 会话元数据
     */
    private static class SessionMetadata {
        private final String sessionId;
        private final String username;
        private final long startTime;

        public SessionMetadata(String sessionId, String username) {
            this.sessionId = sessionId;
            this.username = username;
            this.startTime = System.currentTimeMillis();
        }
    }
}
