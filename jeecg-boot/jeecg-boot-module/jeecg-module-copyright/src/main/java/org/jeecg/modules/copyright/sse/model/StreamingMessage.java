package org.jeecg.modules.copyright.sse.model;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.Date;
import java.util.Map;

/**
 * SSE流式消息模型
 *
 * 用于前后端SSE通信的统一消息格式
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StreamingMessage implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 消息类型
     * - chat: 聊天消息
     * - status: 状态更新
     * - progress: 进度更新
     * - error: 错误消息
     * - done: 完成消息
     */
    private String type;

    /**
     * 会话ID
     */
    private String sessionId;

    /**
     * 消息内容
     */
    private String content;

    /**
     * 扩展数据(可选)
     */
    private Map<String, Object> data;

    /**
     * 时间戳
     */
    @JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    private Date timestamp;

    /**
     * 创建聊天消息
     */
    public static StreamingMessage chat(String sessionId, String content) {
        return StreamingMessage.builder()
                .type("chat")
                .sessionId(sessionId)
                .content(content)
                .timestamp(new Date())
                .build();
    }

    /**
     * 创建状态消息
     */
    public static StreamingMessage status(String sessionId, String status) {
        return StreamingMessage.builder()
                .type("status")
                .sessionId(sessionId)
                .content(status)
                .timestamp(new Date())
                .build();
    }

    /**
     * 创建进度消息
     */
    public static StreamingMessage progress(String sessionId, String progress, Map<String, Object> data) {
        return StreamingMessage.builder()
                .type("progress")
                .sessionId(sessionId)
                .content(progress)
                .data(data)
                .timestamp(new Date())
                .build();
    }

    /**
     * 创建错误消息
     */
    public static StreamingMessage error(String sessionId, String errorMessage) {
        return StreamingMessage.builder()
                .type("error")
                .sessionId(sessionId)
                .content(errorMessage)
                .timestamp(new Date())
                .build();
    }

    /**
     * 创建完成消息
     */
    public static StreamingMessage done(String sessionId) {
        return StreamingMessage.builder()
                .type("done")
                .sessionId(sessionId)
                .content("Stream completed")
                .timestamp(new Date())
                .build();
    }
}
