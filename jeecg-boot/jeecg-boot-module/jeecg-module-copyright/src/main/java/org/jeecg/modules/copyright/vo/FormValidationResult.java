package org.jeecg.modules.copyright.vo;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 表格验证结果
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FormValidationResult {

    /**
     * 是否验证通过
     */
    @JsonProperty("isValid")
    @JsonPropertyDescription("表格是否验证通过")
    private Boolean isValid;

    /**
     * 缺失字段
     */
    @JsonProperty("missingFields")
    @JsonPropertyDescription("缺失的必填字段列表")
    private List<String> missingFields;

    /**
     * 验证错误
     */
    @JsonProperty("validationErrors")
    @JsonPropertyDescription("验证错误列表")
    private List<String> validationErrors;

    /**
     * 文件路径
     */
    @JsonProperty("filePath")
    @JsonPropertyDescription("生成的表格文件路径")
    private String filePath;

    /**
     * 会话ID
     */
    @JsonProperty("sessionId")
    @JsonPropertyDescription("会话ID")
    private String sessionId;
}
