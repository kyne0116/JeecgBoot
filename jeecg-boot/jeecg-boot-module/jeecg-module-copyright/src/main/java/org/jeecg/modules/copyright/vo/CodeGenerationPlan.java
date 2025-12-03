package org.jeecg.modules.copyright.vo;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 代码生成计划
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CodeGenerationPlan {

    /**
     * 模块列表
     */
    @JsonProperty("modules")
    @JsonPropertyDescription("代码模块列表,包含实体、DAO、Service、Controller等")
    private List<CodeModule> modules;

    /**
     * 预估总行数
     */
    @JsonProperty("estimatedLines")
    @JsonPropertyDescription("预估生成的总代码行数")
    private Integer estimatedLines;

    /**
     * 技术栈
     */
    @JsonProperty("techStack")
    @JsonPropertyDescription("使用的技术栈(Spring Boot、MyBatis-Plus等)")
    private String techStack;

    /**
     * 包名
     */
    @JsonProperty("basePackage")
    @JsonPropertyDescription("代码的基础包名")
    private String basePackage;

    /**
     * 代码模块
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CodeModule {
        /**
         * 模块名称
         */
        @JsonProperty("moduleName")
        @JsonPropertyDescription("模块名称(如UserModule)")
        private String moduleName;

        /**
         * 模块类型
         */
        @JsonProperty("moduleType")
        @JsonPropertyDescription("模块类型(entity/dao/service/controller/util)")
        private String moduleType;

        /**
         * 文件列表
         */
        @JsonProperty("files")
        @JsonPropertyDescription("该模块包含的文件列表")
        private List<String> files;

        /**
         * 预估行数
         */
        @JsonProperty("estimatedLines")
        @JsonPropertyDescription("该模块预估的代码行数")
        private Integer estimatedLines;
    }
}
