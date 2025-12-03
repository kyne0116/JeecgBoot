package org.jeecg.modules.copyright.vo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Agent编排执行结果
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OrchestratorResult {

    /**
     * 执行是否成功
     */
    private Boolean success;

    /**
     * 会话ID
     */
    private String sessionId;

    /**
     * 生成的代码结果
     */
    private GeneratedCode generatedCode;

    /**
     * 表格验证结果
     */
    private FormValidationResult formValidationResult;

    /**
     * 文档验证结果
     */
    private DocumentValidationResult documentValidationResult;

    /**
     * 综合质检报告
     */
    private ComprehensiveQualityReport qualityReport;

    /**
     * 总执行时长(毫秒)
     */
    private Long totalDurationMs;

    /**
     * 质检轮次
     */
    private Integer qualityCheckRounds;

    /**
     * 失败原因
     */
    private String failureReason;
}
