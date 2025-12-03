package org.jeecg.modules.copyright.agent.orchestrator;

import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.agent.core.AgentContext;
import org.jeecg.modules.copyright.agent.core.AgentResult;
import org.jeecg.modules.copyright.agent.impl.*;
import org.jeecg.modules.copyright.vo.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * Agent编排器
 * <p>
 * 负责协调5个Agent的执行流程:
 * 1. ReactClarifyAgent -> 等待需求澄清完成
 * 2. 并行执行: ReactCodeGenAgent + ReactFormFillAgent + ReactDocWriterAgent
 * 3. ReactQualityCheckAgent -> 质量检查(最多2次重试)
 * 4. 更新会话状态和进度
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Component
@Slf4j
public class CopyrightAgentOrchestrator {

    @Autowired
    private ReactClarifyAgent clarifyAgent;

    @Autowired
    private ReactCodeGenAgent codeGenAgent;

    @Autowired
    private ReactFormFillAgent formFillAgent;

    @Autowired
    private ReactDocWriterAgent docWriterAgent;

    @Autowired
    private ReactQualityCheckAgent qualityCheckAgent;

    private static final int MAX_QUALITY_CHECK_ROUNDS = 2;

    /**
     * 执行完整的软著申报材料生成流程
     *
     * @param context Agent执行上下文
     * @return 编排执行结果
     */
    public OrchestratorResult orchestrate(AgentContext context) {
        log.info("[CopyrightAgentOrchestrator] 开始编排执行, sessionId: {}", context.getSessionId());

        long startTime = System.currentTimeMillis();

        try {
            // Phase 1: 需求澄清(由外部调用完成)
            CopyrightRequirement requirement = context.getRequirement();
            if (requirement == null) {
                return OrchestratorResult.builder()
                        .success(false)
                        .sessionId(context.getSessionId())
                        .failureReason("需求信息未完成澄清")
                        .build();
            }

            log.info("[CopyrightAgentOrchestrator] Phase 1: 需求澄清完成");

            // Phase 2: 并行生成代码、表格、文档
            log.info("[CopyrightAgentOrchestrator] Phase 2: 开始并行生成材料");

            CompletableFuture<GeneratedCode> codeFuture = generateCodeAsync(context);
            CompletableFuture<FormValidationResult> formFuture = generateFormAsync(context);
            CompletableFuture<DocumentValidationResult> docFuture = generateDocAsync(context);

            // 等待所有生成任务完成
            CompletableFuture.allOf(codeFuture, formFuture, docFuture).join();

            GeneratedCode codeResult = codeFuture.join();
            FormValidationResult formResult = formFuture.join();
            DocumentValidationResult docResult = docFuture.join();

            log.info("[CopyrightAgentOrchestrator] Phase 2: 材料生成完成");

            // Phase 3: 质量检查循环(最多2次)
            ComprehensiveQualityReport qualityReport = null;
            int checkRound = 1;

            while (checkRound <= MAX_QUALITY_CHECK_ROUNDS) {
                log.info("[CopyrightAgentOrchestrator] Phase 3: 第{}轮质量检查", checkRound);

                qualityReport = performQualityCheck(context, codeResult, formResult, docResult, checkRound);

                if (qualityReport.getOverallPassed()) {
                    log.info("[CopyrightAgentOrchestrator] 质量检查通过,流程完成");
                    break;
                }

                if (checkRound >= MAX_QUALITY_CHECK_ROUNDS) {
                    log.warn("[CopyrightAgentOrchestrator] 达到最大重试次数,质量检查未通过");
                    break;
                }

                // 重新生成失败的组件
                List<String> componentsToRegenerate = qualityReport.getComponentsToRegenerate();
                log.info("[CopyrightAgentOrchestrator] 需要重新生成: {}", componentsToRegenerate);

                if (componentsToRegenerate.contains("code")) {
                    codeResult = regenerateCode(context);
                }
                if (componentsToRegenerate.contains("form")) {
                    formResult = regenerateForm(context);
                }
                if (componentsToRegenerate.contains("document")) {
                    docResult = regenerateDocument(context);
                }

                checkRound++;
            }

            // Phase 4: 构建结果
            long endTime = System.currentTimeMillis();
            long totalDuration = endTime - startTime;

            OrchestratorResult result = OrchestratorResult.builder()
                    .success(qualityReport != null && qualityReport.getOverallPassed())
                    .sessionId(context.getSessionId())
                    .generatedCode(codeResult)
                    .formValidationResult(formResult)
                    .documentValidationResult(docResult)
                    .qualityReport(qualityReport)
                    .totalDurationMs(totalDuration)
                    .qualityCheckRounds(checkRound)
                    .build();

            log.info("[CopyrightAgentOrchestrator] 编排执行完成 - 成功:{}, 耗时:{}ms, 质检轮次:{}",
                    result.getSuccess(), totalDuration, checkRound);

            return result;

        } catch (Exception e) {
            log.error("[CopyrightAgentOrchestrator] 编排执行失败", e);

            long endTime = System.currentTimeMillis();

            return OrchestratorResult.builder()
                    .success(false)
                    .sessionId(context.getSessionId())
                    .failureReason("编排执行失败: " + e.getMessage())
                    .totalDurationMs(endTime - startTime)
                    .build();
        }
    }

    /**
     * 异步生成代码
     */
    @Async
    public CompletableFuture<GeneratedCode> generateCodeAsync(AgentContext context) {
        log.info("[CopyrightAgentOrchestrator] 异步生成代码");

        try {
            AgentResult result = codeGenAgent.execute(context);
            if (result.isSuccess()) {
                return CompletableFuture.completedFuture((GeneratedCode) result.getData());
            } else {
                log.error("[CopyrightAgentOrchestrator] 代码生成失败: {}", result.getMessage());
                return CompletableFuture.completedFuture(null);
            }
        } catch (Exception e) {
            log.error("[CopyrightAgentOrchestrator] 代码生成异常", e);
            return CompletableFuture.completedFuture(null);
        }
    }

    /**
     * 异步生成表格
     */
    @Async
    public CompletableFuture<FormValidationResult> generateFormAsync(AgentContext context) {
        log.info("[CopyrightAgentOrchestrator] 异步生成表格");

        try {
            AgentResult result = formFillAgent.execute(context);
            if (result.isSuccess()) {
                return CompletableFuture.completedFuture((FormValidationResult) result.getData());
            } else {
                log.error("[CopyrightAgentOrchestrator] 表格生成失败: {}", result.getMessage());
                return CompletableFuture.completedFuture(null);
            }
        } catch (Exception e) {
            log.error("[CopyrightAgentOrchestrator] 表格生成异常", e);
            return CompletableFuture.completedFuture(null);
        }
    }

    /**
     * 异步生成文档
     */
    @Async
    public CompletableFuture<DocumentValidationResult> generateDocAsync(AgentContext context) {
        log.info("[CopyrightAgentOrchestrator] 异步生成文档");

        try {
            AgentResult result = docWriterAgent.execute(context);
            if (result.isSuccess()) {
                return CompletableFuture.completedFuture((DocumentValidationResult) result.getData());
            } else {
                log.error("[CopyrightAgentOrchestrator] 文档生成失败: {}", result.getMessage());
                return CompletableFuture.completedFuture(null);
            }
        } catch (Exception e) {
            log.error("[CopyrightAgentOrchestrator] 文档生成异常", e);
            return CompletableFuture.completedFuture(null);
        }
    }

    /**
     * 执行质量检查
     */
    private ComprehensiveQualityReport performQualityCheck(
            AgentContext context,
            GeneratedCode codeResult,
            FormValidationResult formResult,
            DocumentValidationResult docResult,
            int checkRound) {

        // 准备质检上下文
        Map<String, Object> params = new HashMap<>(context.getParams());
        params.put("codeResult", codeResult);
        params.put("formResult", formResult);
        params.put("docResult", docResult);
        params.put("checkRound", checkRound);

        AgentContext qualityCheckContext = AgentContext.builder()
                .sessionId(context.getSessionId())
                .userId(context.getUserId())
                .requirement(context.getRequirement())
                .params(params)
                .build();

        AgentResult result = qualityCheckAgent.execute(qualityCheckContext);

        if (result.isSuccess()) {
            return (ComprehensiveQualityReport) result.getData();
        } else {
            log.error("[CopyrightAgentOrchestrator] 质量检查失败: {}", result.getMessage());
            return ComprehensiveQualityReport.builder()
                    .overallPassed(false)
                    .sessionId(context.getSessionId())
                    .checkRound(checkRound)
                    .build();
        }
    }

    /**
     * 重新生成代码
     */
    private GeneratedCode regenerateCode(AgentContext context) {
        log.info("[CopyrightAgentOrchestrator] 重新生成代码");
        return generateCodeAsync(context).join();
    }

    /**
     * 重新生成表格
     */
    private FormValidationResult regenerateForm(AgentContext context) {
        log.info("[CopyrightAgentOrchestrator] 重新生成表格");
        return generateFormAsync(context).join();
    }

    /**
     * 重新生成文档
     */
    private DocumentValidationResult regenerateDocument(AgentContext context) {
        log.info("[CopyrightAgentOrchestrator] 重新生成文档");
        return generateDocAsync(context).join();
    }
}
