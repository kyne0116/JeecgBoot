package org.jeecg.modules.ai.vo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 消息事件数据
 *
 * @author chenrui
 * @date 2024/12/03
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EventMessageData {

    /**
     * 消息内容
     */
    private String message;

    /**
     * 消息类型（text, image, tool_call 等）
     */
    private String messageType;

    /**
     * 是否完成
     */
    private Boolean isComplete;

    /**
     * 额外数据
     */
    private Object extraData;
}
