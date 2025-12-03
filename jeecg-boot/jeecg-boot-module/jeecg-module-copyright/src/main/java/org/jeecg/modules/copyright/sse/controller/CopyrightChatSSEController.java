package org.jeecg.modules.copyright.sse.controller;

import lombok.extern.slf4j.Slf4j;
import org.jeecg.common.api.vo.Result;
import org.jeecg.modules.copyright.agent.service.ReactClarifyAgentSSEService;
import org.jeecg.modules.copyright.apply.entity.CopyrightMessage;
import org.jeecg.modules.copyright.apply.service.ICopyrightMessageService;
import org.jeecg.modules.copyright.apply.service.ICopyrightSessionService;
import org.jeecg.modules.copyright.sse.manager.SseEmitterManager;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.messages.Message;
import org.springframework.ai.chat.messages.SystemMessage;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.scheduling.annotation.Async;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import reactor.core.publisher.Flux;

import java.util.ArrayList;
import java.util.List;

/**
 * 软著申报聊天SSE流式响应Controller
 *
 * 提供SSE流式响应端点，实现与ChatGPT相同的逐字显示体验
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@RestController
@RequestMapping("/copyright/chat")
@Slf4j
public class CopyrightChatSSEController {

    @Autowired
    private SseEmitterManager emitterManager;

    @Autowired
    private ICopyrightMessageService messageService;

    @Autowired
    private ICopyrightSessionService sessionService;

    @Autowired
    private ReactClarifyAgentSSEService clarifyAgentService;

    @Autowired
    private ChatModel chatModel;

    /**
     * 系统提示词 - 软著申报需求澄清
     */
    private static final String SYSTEM_PROMPT = """
            你是一个专业的软著申报需求澄清助手。你的任务是通过多轮对话,收集用户的软著申报需求信息。

            必须收集的9个核心信息：
            1. 软件全称和简称
            2. 软件版本号
            3. 软件分类（应用软件/系统软件/支撑软件/嵌入式软件）
            4. 主要编程语言
            5. 技术架构描述
            6. 核心功能列表（至少3个）
            7. 技术创新点（至少2个）
            8. 申请人信息（企业/个人）
            9. 开发完成日期

            对话原则：
            - 每次只询问1-2个相关问题，避免一次性询问太多
            - 根据用户回答，灵活调整问题顺序
            - 用简洁、友好的语言沟通
            - 当收集完所有信息后，总结确认

            注意：你只负责收集需求，不生成代码和文档。
            """;

    /**
     * SSE流式响应端点
     *
     * 前端使用: new EventSource('/copyright/chat/stream?sessionId=xxx&username=admin')
     *
     * @param sessionId 会话ID
     * @param username  用户名
     * @return SseEmitter
     */
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter stream(@RequestParam String sessionId,
                            @RequestParam String username) {
        log.info("[CopyrightChatSSEController] 建立SSE连接, sessionId: {}, username: {}",
                sessionId, username);

        // 创建SSE Emitter
        SseEmitter emitter = emitterManager.createEmitter(sessionId);

        // 发送欢迎消息
        emitterManager.sendStatus(sessionId, "SSE连接成功，可以开始对话了!");

        return emitter;
    }

    /**
     * 接收用户消息（HTTP POST）
     *
     * 用户输入通过POST发送，AI响应通过SSE流式推送
     *
     * @param sessionId 会话ID
     * @param username  用户名
     * @param message   用户消息
     * @param isFirstMessage 是否为首条消息（首条消息启动ReactClarifyAgent流程）
     * @return Result
     */
    @PostMapping("/message")
    public Result<?> sendMessage(@RequestParam String sessionId,
                                   @RequestParam String username,
                                   @RequestParam String message,
                                   @RequestParam(defaultValue = "false") boolean isFirstMessage) {
        log.info("[CopyrightChatSSEController] 接收用户消息, sessionId: {}, user: {}, isFirst: {}, message: {}",
                sessionId, username, isFirstMessage, message);

        try {
            // 1. 检查SSE连接是否在线
            if (!emitterManager.isOnline(sessionId)) {
                return Result.error("SSE连接已断开，请重新建立连接");
            }

            // 2. 判断是首条消息还是后续消息
            if (isFirstMessage) {
                // 首条消息：启动ReactClarifyAgent流程
                log.info("[CopyrightChatSSEController] 首条消息，启动ReactClarifyAgent流程");

                // 异步启动需求澄清流程
                clarifyAgentService.startClarification(sessionId, username, message);

                return Result.OK("需求澄清流程已启动，请等待AI回复...");

            } else {
                // 后续消息：提交到用户输入队列
                log.info("[CopyrightChatSSEController] 后续消息，提交到输入队列");

                boolean success = clarifyAgentService.submitUserInput(sessionId, message);

                if (success) {
                    return Result.OK("消息已接收，正在处理中...");
                } else {
                    return Result.error("消息提交失败，会话可能已结束");
                }
            }

        } catch (Exception e) {
            log.error("[CopyrightChatSSEController] 处理消息失败", e);
            emitterManager.sendError(sessionId, "消息处理失败: " + e.getMessage());
            return Result.error("消息处理失败: " + e.getMessage());
        }
    }

    /**
     * 异步处理用户消息，通过SSE流式推送AI响应
     *
     * @param sessionId 会话ID
     * @param userMessage 用户消息
     */
    @Async
    public void processMessageAsync(String sessionId, String userMessage) {
        log.info("[CopyrightChatSSEController] 开始异步处理消息, sessionId: {}", sessionId);

        try {
            // 1. 推送状态：正在思考
            emitterManager.sendStatus(sessionId, "正在思考...");

            // 2. 构建对话历史
            List<Message> messages = buildChatHistory(sessionId);

            // 3. 添加当前用户消息
            messages.add(new UserMessage(userMessage));

            // 4. 创建Prompt
            Prompt prompt = new Prompt(messages);

            // 5. 流式调用LLM
            Flux<ChatResponse> stream = chatModel.stream(prompt);

            // 6. 收集完整响应（用于保存到数据库）
            StringBuilder fullResponse = new StringBuilder();

            // 7. 订阅流式响应，逐字推送
            stream.subscribe(
                    chatResponse -> {
                        // 获取增量内容
                        String delta = chatResponse.getResult().getOutput().getText();
                        if (delta != null && !delta.isEmpty()) {
                            // 追加到完整响应
                            fullResponse.append(delta);
                            // 通过SSE推送
                            emitterManager.sendChat(sessionId, delta);
                        }
                    },
                    error -> {
                        // 错误处理
                        log.error("[CopyrightChatSSEController] 流式响应错误: " + sessionId, error);
                        emitterManager.sendError(sessionId, "AI响应失败: " + error.getMessage());
                        emitterManager.sendStatus(sessionId, "对话已结束");
                    },
                    () -> {
                        // 完成处理
                        log.info("[CopyrightChatSSEController] 流式响应完成, sessionId: {}, responseLength: {}",
                                sessionId, fullResponse.length());

                        // 保存AI响应到数据库
                        if (fullResponse.length() > 0) {
                            messageService.saveMessage(sessionId, "assistant", fullResponse.toString());
                        }

                        // 推送完成状态
                        emitterManager.sendStatus(sessionId, "思考完成");

                        // TODO: 检查需求是否收集完成，如果完成则更新会话状态
                    }
            );

        } catch (Exception e) {
            log.error("[CopyrightChatSSEController] 异步处理消息失败: " + sessionId, e);
            emitterManager.sendError(sessionId, "处理失败: " + e.getMessage());
        }
    }

    /**
     * 构建对话历史
     *
     * @param sessionId 会话ID
     * @return 对话消息列表
     */
    private List<Message> buildChatHistory(String sessionId) {
        List<Message> messages = new ArrayList<>();

        // 1. 添加系统提示词
        messages.add(new SystemMessage(SYSTEM_PROMPT));

        // 2. 从数据库获取历史消息
        List<CopyrightMessage> historyMessages = messageService.getSessionMessages(sessionId);

        // 3. 转换为Spring AI Message格式
        for (CopyrightMessage msg : historyMessages) {
            if ("user".equals(msg.getRole())) {
                messages.add(new UserMessage(msg.getContent()));
            } else if ("assistant".equals(msg.getRole())) {
                messages.add(new AssistantMessage(msg.getContent()));
            }
        }

        log.debug("[CopyrightChatSSEController] 构建对话历史完成, sessionId: {}, messageCount: {}",
                sessionId, messages.size());

        return messages;
    }

    /**
     * 关闭SSE连接
     *
     * @param sessionId 会话ID
     * @return Result
     */
    @DeleteMapping("/stream")
    public Result<?> closeStream(@RequestParam String sessionId) {
        log.info("[CopyrightChatSSEController] 关闭SSE连接, sessionId: {}", sessionId);
        emitterManager.close(sessionId);
        return Result.OK("连接已关闭");
    }

    /**
     * 获取SSE连接状态
     *
     * @param sessionId 会话ID
     * @return Result
     */
    @GetMapping("/stream/status")
    public Result<?> getStreamStatus(@RequestParam String sessionId) {
        boolean online = emitterManager.isOnline(sessionId);
        return Result.OK(online ? "在线" : "离线");
    }
}
