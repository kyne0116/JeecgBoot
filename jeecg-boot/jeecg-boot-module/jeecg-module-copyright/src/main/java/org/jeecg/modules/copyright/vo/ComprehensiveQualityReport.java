package org.jeecg.modules.copyright.vo;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 综合质检报告
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ComprehensiveQualityReport {

    /**
     * 整体是否通过
     */
    @JsonProperty("overallPassed")
    @JsonPropertyDescription("整体质检是否通过")
    private Boolean overallPassed;

    /**
     * 代码质量报告
     */
    @JsonProperty("codeQualityReport")
    @JsonPropertyDescription("代码质量检查报告")
    private CodeQualityReport codeQualityReport;

    /**
     * 表格验证结果
     */
    @JsonProperty("formValidationResult")
    @JsonPropertyDescription("表格验证结果")
    private FormValidationResult formValidationResult;

    /**
     * 文档验证结果
     */
    @JsonProperty("documentValidationResult")
    @JsonPropertyDescription("文档验证结果")
    private DocumentValidationResult documentValidationResult;

    /**
     * 需要重新生成的组件列表
     */
    @JsonProperty("componentsToRegenerate")
    @JsonPropertyDescription("需要重新生成的组件列表(code/form/document)")
    private List<String> componentsToRegenerate;

    /**
     * 质检建议
     */
    @JsonProperty("suggestions")
    @JsonPropertyDescription("质检建议和改进意见")
    private List<String> suggestions;

    /**
     * 会话ID
     */
    @JsonProperty("sessionId")
    @JsonPropertyDescription("会话ID")
    private String sessionId;

    /**
     * 质检轮次
     */
    @JsonProperty("checkRound")
    @JsonPropertyDescription("质检轮次(1-3)")
    private Integer checkRound;
}
