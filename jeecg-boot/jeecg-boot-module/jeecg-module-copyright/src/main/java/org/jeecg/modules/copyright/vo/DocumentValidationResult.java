package org.jeecg.modules.copyright.vo;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 文档验证结果
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DocumentValidationResult {

    /**
     * 是否验证通过
     */
    @JsonProperty("isValid")
    @JsonPropertyDescription("文档是否验证通过")
    private Boolean isValid;

    /**
     * 文档字数
     */
    @JsonProperty("wordCount")
    @JsonPropertyDescription("文档字数(不含标点和空格)")
    private Integer wordCount;

    /**
     * 是否符合字数要求
     */
    @JsonProperty("meetsWordCountRequirement")
    @JsonPropertyDescription("是否符合3000-5000字要求")
    private Boolean meetsWordCountRequirement;

    /**
     * 章节完整性
     */
    @JsonProperty("sectionsComplete")
    @JsonPropertyDescription("章节是否完整")
    private Boolean sectionsComplete;

    /**
     * 缺失章节
     */
    @JsonProperty("missingSections")
    @JsonPropertyDescription("缺失的章节列表")
    private List<String> missingSections;

    /**
     * 文件路径
     */
    @JsonProperty("filePath")
    @JsonPropertyDescription("生成的文档文件路径")
    private String filePath;

    /**
     * Markdown内容
     */
    @JsonProperty("markdownContent")
    @JsonPropertyDescription("Markdown原始内容")
    private String markdownContent;

    /**
     * 会话ID
     */
    @JsonProperty("sessionId")
    @JsonPropertyDescription("会话ID")
    private String sessionId;
}
