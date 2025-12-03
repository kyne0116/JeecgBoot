package org.jeecg.modules.copyright.sse.manager;

import com.alibaba.fastjson.JSON;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.sse.model.StreamingMessage;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * SSE Emitter管理器
 *
 * 负责管理会话ID与SseEmitter的映射关系
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Component
@Slf4j
public class SseEmitterManager {

    /**
     * 会话ID -> SseEmitter映射
     */
    private final Map<String, SseEmitter> emitters = new ConcurrentHashMap<>();

    /**
     * SSE连接超时时间 (30分钟)
     */
    private static final long TIMEOUT = 30 * 60 * 1000L;

    /**
     * 创建SSE Emitter
     *
     * @param sessionId 会话ID
     * @return SseEmitter
     */
    public SseEmitter createEmitter(String sessionId) {
        // 移除旧连接(如果存在)
        SseEmitter oldEmitter = emitters.remove(sessionId);
        if (oldEmitter != null) {
            try {
                oldEmitter.complete();
                log.info("[SseEmitterManager] 关闭会话的旧SSE连接: {}", sessionId);
            } catch (Exception e) {
                log.warn("[SseEmitterManager] 关闭旧连接失败: {}", e.getMessage());
            }
        }

        // 创建新连接
        SseEmitter emitter = new SseEmitter(TIMEOUT);

        // 设置回调
        emitter.onCompletion(() -> {
            emitters.remove(sessionId);
            log.info("[SseEmitterManager] SSE连接完成: {}", sessionId);
        });

        emitter.onTimeout(() -> {
            emitters.remove(sessionId);
            log.warn("[SseEmitterManager] SSE连接超时: {}", sessionId);
        });

        emitter.onError(throwable -> {
            emitters.remove(sessionId);
            log.error("[SseEmitterManager] SSE连接错误: " + sessionId, throwable);
        });

        // 保存连接
        emitters.put(sessionId, emitter);
        log.info("[SseEmitterManager] 创建SSE连接: {}, 当前连接数: {}", sessionId, emitters.size());

        return emitter;
    }

    /**
     * 发送消息
     *
     * @param sessionId 会话ID
     * @param message   消息对象
     * @return 是否发送成功
     */
    public boolean send(String sessionId, StreamingMessage message) {
        SseEmitter emitter = emitters.get(sessionId);
        if (emitter == null) {
            log.warn("[SseEmitterManager] SSE连接不存在: {}", sessionId);
            return false;
        }

        try {
            emitter.send(SseEmitter.event()
                    .name(message.getType())
                    .data(JSON.toJSONString(message)));
            log.debug("[SseEmitterManager] 发送消息成功: sessionId={}, type={}", sessionId, message.getType());
            return true;
        } catch (IOException e) {
            log.error("[SseEmitterManager] 发送消息失败: " + sessionId, e);
            emitters.remove(sessionId);
            return false;
        }
    }

    /**
     * 发送聊天消息
     *
     * @param sessionId 会话ID
     * @param content   消息内容
     * @return 是否发送成功
     */
    public boolean sendChat(String sessionId, String content) {
        return send(sessionId, StreamingMessage.chat(sessionId, content));
    }

    /**
     * 发送状态消息
     *
     * @param sessionId 会话ID
     * @param status    状态
     * @return 是否发送成功
     */
    public boolean sendStatus(String sessionId, String status) {
        return send(sessionId, StreamingMessage.status(sessionId, status));
    }

    /**
     * 发送错误消息
     *
     * @param sessionId    会话ID
     * @param errorMessage 错误信息
     * @return 是否发送成功
     */
    public boolean sendError(String sessionId, String errorMessage) {
        return send(sessionId, StreamingMessage.error(sessionId, errorMessage));
    }

    /**
     * 完成SSE连接
     *
     * @param sessionId 会话ID
     */
    public void complete(String sessionId) {
        SseEmitter emitter = emitters.remove(sessionId);
        if (emitter != null) {
            try {
                // 发送完成消息
                emitter.send(SseEmitter.event()
                        .name("done")
                        .data(JSON.toJSONString(StreamingMessage.done(sessionId))));
                // 完成连接
                emitter.complete();
                log.info("[SseEmitterManager] SSE连接完成: {}", sessionId);
            } catch (IOException e) {
                log.error("[SseEmitterManager] 完成连接失败: " + sessionId, e);
            }
        }
    }

    /**
     * 关闭SSE连接
     *
     * @param sessionId 会话ID
     */
    public void close(String sessionId) {
        SseEmitter emitter = emitters.remove(sessionId);
        if (emitter != null) {
            emitter.complete();
            log.info("[SseEmitterManager] 关闭SSE连接: {}", sessionId);
        }
    }

    /**
     * 检查会话是否在线
     *
     * @param sessionId 会话ID
     * @return true-在线, false-离线
     */
    public boolean isOnline(String sessionId) {
        return emitters.containsKey(sessionId);
    }

    /**
     * 获取在线连接数
     *
     * @return 在线连接数
     */
    public int getOnlineCount() {
        return emitters.size();
    }
}
