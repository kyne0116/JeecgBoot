package org.jeecg.modules.copyright.vo;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.List;

/**
 * 需求完整性检查请求对象
 * 用于requirementCheckTool工具函数的输入参数
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RequirementCheckRequest implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 软件全称
     */
    @JsonProperty("softwareName")
    @JsonPropertyDescription("软件的完整名称")
    private String softwareName;

    /**
     * 软件简称
     */
    @JsonProperty("shortName")
    @JsonPropertyDescription("软件的简称或缩写")
    private String shortName;

    /**
     * 软件版本号
     */
    @JsonProperty("version")
    @JsonPropertyDescription("软件版本号,例如v1.0、v2.1等")
    private String version;

    /**
     * 软件分类
     */
    @JsonProperty("category")
    @JsonPropertyDescription("软件分类:应用软件、系统软件、支撑软件、嵌入式软件")
    private String category;

    /**
     * 主要编程语言
     */
    @JsonProperty("codeLanguage")
    @JsonPropertyDescription("主要编程语言,例如Java、Python、C++等")
    private String codeLanguage;

    /**
     * 技术架构
     */
    @JsonProperty("techStack")
    @JsonPropertyDescription("技术架构描述,例如Spring Boot + Vue3")
    private String techStack;

    /**
     * 核心功能列表
     */
    @JsonProperty("features")
    @JsonPropertyDescription("核心功能列表,至少3个功能")
    private List<String> features;

    /**
     * 技术创新点列表
     */
    @JsonProperty("innovations")
    @JsonPropertyDescription("技术创新点列表,至少2个创新点")
    private List<String> innovations;

    /**
     * 申请人信息
     */
    @JsonProperty("applicantName")
    @JsonPropertyDescription("申请人名称(企业名称或个人姓名)")
    private String applicantName;
}
