package org.jeecg.modules.ai.vo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 错误事件数据
 *
 * @author chenrui
 * @date 2024/12/03
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EventErrorData {

    /**
     * 错误消息
     */
    private String message;

    /**
     * 错误代码
     */
    private String errorCode;

    /**
     * 是否成功
     */
    private Boolean success;

    /**
     * 错误详情
     */
    private String detail;

    /**
     * 错误类型（timeout, model_error, network_error 等）
     */
    private String errorType;
}
