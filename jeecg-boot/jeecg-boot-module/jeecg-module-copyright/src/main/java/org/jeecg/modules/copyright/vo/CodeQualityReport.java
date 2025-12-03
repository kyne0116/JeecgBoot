package org.jeecg.modules.copyright.vo;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 代码质量报告
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CodeQualityReport {

    /**
     * 总行数
     */
    @JsonProperty("totalLines")
    @JsonPropertyDescription("总代码行数")
    private Integer totalLines;

    /**
     * 有效行数
     */
    @JsonProperty("effectiveLines")
    @JsonPropertyDescription("有效代码行数(去除空行和注释)")
    private Integer effectiveLines;

    /**
     * 是否符合要求
     */
    @JsonProperty("meetsRequirement")
    @JsonPropertyDescription("是否符合5000-6000行要求")
    private Boolean meetsRequirement;

    /**
     * 代码结构完整性
     */
    @JsonProperty("structureComplete")
    @JsonPropertyDescription("代码结构是否完整(实体、DAO、Service、Controller等)")
    private Boolean structureComplete;

    /**
     * 质量问题
     */
    @JsonProperty("issues")
    @JsonPropertyDescription("发现的质量问题列表")
    private List<QualityIssue> issues;

    /**
     * 建议调整
     */
    @JsonProperty("suggestions")
    @JsonPropertyDescription("代码调整建议")
    private List<String> suggestions;

    /**
     * 质量问题
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class QualityIssue {
        /**
         * 问题类型
         */
        @JsonProperty("issueType")
        @JsonPropertyDescription("问题类型(line_count/structure/syntax)")
        private String issueType;

        /**
         * 问题描述
         */
        @JsonProperty("description")
        @JsonPropertyDescription("问题描述")
        private String description;

        /**
         * 严重级别
         */
        @JsonProperty("severity")
        @JsonPropertyDescription("严重级别(high/medium/low)")
        private String severity;
    }
}
