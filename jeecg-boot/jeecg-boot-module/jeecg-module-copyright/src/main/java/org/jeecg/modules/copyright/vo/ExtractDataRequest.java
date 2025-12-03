package org.jeecg.modules.copyright.vo;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

/**
 * 数据提取请求对象
 * 用于extractDataTool工具函数的输入参数
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExtractDataRequest implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 对话历史文本(包含用户和助手的多轮对话)
     */
    @JsonProperty("conversationText")
    @JsonPropertyDescription("多轮对话的完整文本内容,包含用户提供的所有软著申报信息")
    private String conversationText;

    /**
     * 会话ID(可选,用于日志追踪)
     */
    @JsonProperty("sessionId")
    @JsonPropertyDescription("当前会话的唯一标识")
    private String sessionId;
}
