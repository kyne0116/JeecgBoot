package org.jeecg.modules.copyright.vo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.List;

/**
 * 软著申报需求对象
 * 由ReactClarifyAgent通过多轮对话收集并生成
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CopyrightRequirement implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 软件全称
     */
    private String softwareName;

    /**
     * 软件简称
     */
    private String shortName;

    /**
     * 软件版本号(例如: v1.0)
     */
    private String version;

    /**
     * 软件分类(应用软件/系统软件/支撑软件/嵌入式软件)
     */
    private String category;

    /**
     * 主要编程语言(例如: Java、Python、C++)
     */
    private String codeLanguage;

    /**
     * 技术架构描述(例如: Spring Boot + Vue3)
     */
    private String techStack;

    /**
     * 核心功能列表(至少3个)
     */
    private List<SoftwareFeature> features;

    /**
     * 技术创新点列表(至少2个)
     */
    private List<String> innovations;

    /**
     * 系统架构描述
     */
    private String architecture;

    /**
     * 申请人信息
     */
    private ApplicantInfo applicant;

    /**
     * 开发完成日期(格式: yyyy-MM-dd)
     */
    private String devCompleteDate;

    /**
     * 软件功能对象
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SoftwareFeature implements Serializable {
        /**
         * 功能名称
         */
        private String name;

        /**
         * 功能详细描述
         */
        private String description;
    }

    /**
     * 申请人信息对象
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ApplicantInfo implements Serializable {
        /**
         * 申请人名称(企业名称或个人姓名)
         */
        private String name;

        /**
         * 申请人类型(enterprise:企业 / individual:个人)
         */
        private String type;
    }
}
