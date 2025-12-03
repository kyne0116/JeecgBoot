package org.jeecg.modules.ai.vo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * SSE 事件数据封装类
 *
 * @author chenrui
 * @date 2024/12/03
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EventData {

    /**
     * 事件类型常量
     */
    public static final String EVENT_INIT_REQUEST_ID = "init_request_id";  // 初始化请求ID
    public static final String EVENT_MESSAGE = "message";                   // 部分消息
    public static final String EVENT_MESSAGE_END = "message_end";           // 消息结束
    public static final String EVENT_ERROR = "error";                       // 错误
    public static final String EVENT_THINKING = "thinking";                 // AI思考过程
    public static final String EVENT_THINKING_END = "thinking_end";         // 思考结束

    /**
     * 请求唯一标识
     */
    private String requestId;

    /**
     * 用户ID
     */
    private String userId;

    /**
     * 事件类型
     */
    private String eventType;

    /**
     * 会话ID
     */
    private String conversationId;

    /**
     * 主题ID
     */
    private String topicId;

    /**
     * 事件数据（可以是 EventMessageData 或 EventErrorData）
     */
    private Object data;

    /**
     * 时间戳
     */
    private Long timestamp;

    /**
     * 构造器 - 便捷创建事件
     */
    public EventData(String requestId, String eventType, Object data) {
        this.requestId = requestId;
        this.eventType = eventType;
        this.data = data;
        this.timestamp = System.currentTimeMillis();
    }

    /**
     * 构造器 - 带会话信息
     */
    public EventData(String requestId, String eventType, String conversationId, String topicId, Object data) {
        this.requestId = requestId;
        this.eventType = eventType;
        this.conversationId = conversationId;
        this.topicId = topicId;
        this.data = data;
        this.timestamp = System.currentTimeMillis();
    }
}
