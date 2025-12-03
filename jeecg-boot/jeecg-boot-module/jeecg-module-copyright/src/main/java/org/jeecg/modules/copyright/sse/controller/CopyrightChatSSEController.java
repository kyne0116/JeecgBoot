package org.jeecg.modules.copyright.sse.controller;

import lombok.extern.slf4j.Slf4j;
import org.jeecg.common.api.vo.Result;
import org.jeecg.modules.copyright.apply.service.ICopyrightMessageService;
import org.jeecg.modules.copyright.sse.manager.SseEmitterManager;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

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

    /**
     * SSE流式响应端点
     *
     * 前端使用: new EventSource('/copyright/chat/stream?sessionId=xxx')
     *
     * @param sessionId 会话ID
     * @return SseEmitter
     */
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter stream(@RequestParam String sessionId) {
        log.info("[CopyrightChatSSEController] 建立SSE连接, sessionId: {}", sessionId);

        // 创建SSE Emitter
        SseEmitter emitter = emitterManager.createEmitter(sessionId);

        // 发送欢迎消息
        emitterManager.sendStatus(sessionId, "SSE连接成功，可以开始对话了!");

        // TODO: 后续集成ReactClarifyAgent时，在这里启动流式对话
        // 现在仅返回Emitter，等待后续通过POST接收用户输入后进行处理

        return emitter;
    }

    /**
     * 接收用户消息（HTTP POST）
     *
     * 用户输入通过POST发送，AI响应通过SSE流式推送
     *
     * @param sessionId 会话ID
     * @param message   用户消息
     * @return Result
     */
    @PostMapping("/message")
    public Result<?> sendMessage(@RequestParam String sessionId,
                                   @RequestParam String message) {
        log.info("[CopyrightChatSSEController] 接收用户消息, sessionId: {}, message: {}", sessionId, message);

        try {
            // 1. 保存用户消息到数据库
            messageService.saveMessage(sessionId, "user", message);

            // 2. TODO: 调用ReactClarifyAgent处理消息
            // 目前先返回echo消息
            emitterManager.sendChat(sessionId, "收到您的消息: " + message + " (SSE功能已就绪，等待Agent集成)");

            return Result.OK("消息已发送");
        } catch (Exception e) {
            log.error("[CopyrightChatSSEController] 处理消息失败", e);
            emitterManager.sendError(sessionId, "消息处理失败: " + e.getMessage());
            return Result.error("消息处理失败: " + e.getMessage());
        }
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
