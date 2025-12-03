package org.jeecg.modules.copyright.agent.impl;

import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.agent.core.*;
import org.jeecg.modules.copyright.vo.*;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * ReactQualityCheckAgent - 综合质量检查Agent
 * <p>
 * 对生成的代码、表格、文档进行全面质量检查
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Component
@Slf4j
public class ReactQualityCheckAgent implements CopyrightAgent {

    @Autowired
    private ChatModel chatModel;

    private static final String AGENT_INSTRUCTION = """
            你是一个专业的软著申报材料质量检查专家。你的任务是对生成的三类材料进行全面质量检查。

            检查项目:

            1. 代码质量检查
               - 代码行数是否在5000-6000行之间
               - 代码结构是否完整(Entity、Mapper、Service、Controller)
               - 代码是否可编译通过
               - 代码是否符合Java规范

            2. 表格验证
               - 所有必填字段是否完整
               - 功能列表是否至少3项
               - 格式是否规范
               - 信息是否准确

            3. 文档检查
               - 字数是否在3000-5000字之间
               - 章节结构是否完整(概述、功能、架构、创新、价值)
               - 字体是否为仿宋12号
               - 内容是否专业严谨

            质检标准:
            1. 所有三项材料都必须通过检查
            2. 代码行数必须在要求范围内
            3. 文档字数必须在要求范围内
            4. 不允许有明显的质量问题

            质检流程:
            1. 分别检查代码、表格、文档
            2. 记录发现的问题
            3. 判断是否需要重新生成
            4. 提供改进建议
            5. 生成综合质检报告

            重新生成策略:
            1. 如果某一项不合格,标记该项需要重新生成
            2. 最多允许重新生成2次
            3. 重新生成时要明确指出改进方向
            """;

    @Override
    @LogAgentExecution
    public AgentResult execute(AgentContext context) {
        log.info("[ReactQualityCheckAgent] 开始执行质量检查, sessionId: {}", context.getSessionId());

        try {
            // 从上下文获取各项检查结果
            Object codeResultObj = context.getParams().get("codeResult");
            Object formResultObj = context.getParams().get("formResult");
            Object docResultObj = context.getParams().get("docResult");
            Integer checkRound = (Integer) context.getParams().getOrDefault("checkRound", 1);

            if (codeResultObj == null || formResultObj == null || docResultObj == null) {
                return AgentResult.failure("缺少检查材料,无法进行质量检查");
            }

            // 类型转换
            GeneratedCode codeResult = (GeneratedCode) codeResultObj;
            FormValidationResult formResult = (FormValidationResult) formResultObj;
            DocumentValidationResult docResult = (DocumentValidationResult) docResultObj;

            // 执行综合质检
            ComprehensiveQualityReport report = performComprehensiveCheck(
                    codeResult, formResult, docResult, context.getSessionId(), checkRound);

            log.info("[ReactQualityCheckAgent] 质量检查完成 - 整体通过:{}, 第{}轮检查",
                    report.getOverallPassed(), checkRound);

            return AgentResult.success("质量检查完成", report);

        } catch (Exception e) {
            log.error("[ReactQualityCheckAgent] 质量检查失败", e);
            return AgentResult.failure("质量检查失败: " + e.getMessage());
        }
    }

    /**
     * 执行综合质量检查
     */
    private ComprehensiveQualityReport performComprehensiveCheck(
            GeneratedCode codeResult,
            FormValidationResult formResult,
            DocumentValidationResult docResult,
            String sessionId,
            int checkRound) {

        List<String> componentsToRegenerate = new ArrayList<>();
        List<String> suggestions = new ArrayList<>();

        // 1. 检查代码质量
        CodeQualityReport codeReport = codeResult.getQualityReport();
        if (codeReport != null && !codeReport.getMeetsRequirement()) {
            componentsToRegenerate.add("code");
            suggestions.add("代码质量不符合要求: " + String.join(", ", codeReport.getSuggestions()));
        }

        // 2. 检查表格验证
        if (formResult != null && !formResult.getIsValid()) {
            componentsToRegenerate.add("form");
            suggestions.add("表格填报不完整: " + String.join(", ", formResult.getValidationErrors()));
        }

        // 3. 检查文档验证
        if (docResult != null && !docResult.getIsValid()) {
            componentsToRegenerate.add("document");

            if (!docResult.getMeetsWordCountRequirement()) {
                suggestions.add(String.format("文档字数不符合要求: 当前%d字,需要3000-5000字",
                        docResult.getWordCount()));
            }

            if (!docResult.getSectionsComplete()) {
                suggestions.add("文档章节不完整: 缺少" + String.join(", ", docResult.getMissingSections()));
            }
        }

        // 4. 判断整体是否通过
        boolean overallPassed = componentsToRegenerate.isEmpty();

        // 5. 添加通用建议
        if (!overallPassed) {
            if (checkRound >= 2) {
                suggestions.add("已达到最大重试次数(2次),请人工审核材料");
            } else {
                suggestions.add("建议重新生成不合格的组件: " + String.join(", ", componentsToRegenerate));
            }
        } else {
            suggestions.add("所有材料质量检查通过,符合软著申报要求");
        }

        // 6. 构建综合报告
        return ComprehensiveQualityReport.builder()
                .overallPassed(overallPassed)
                .codeQualityReport(codeReport)
                .formValidationResult(formResult)
                .documentValidationResult(docResult)
                .componentsToRegenerate(componentsToRegenerate)
                .suggestions(suggestions)
                .sessionId(sessionId)
                .checkRound(checkRound)
                .build();
    }

    /**
     * 构建ReactAgent实例
     */
    @SuppressWarnings("unused")
    private ReactAgent buildReactAgent(AgentContext context) {
        log.info("[ReactQualityCheckAgent] 开始构建ReactAgent");

        ReactAgent agent = (ReactAgent) ReactAgent.builder()
                .name("ReactQualityCheckAgent")
                .description("综合质量检查Agent,对代码、表格、文档进行全面检查")
                .instruction(AGENT_INSTRUCTION)
                .model(chatModel)
                .build();

        log.info("[ReactQualityCheckAgent] ReactAgent构建完成");
        return agent;
    }

    @Override
    public String getAgentName() {
        return "ReactQualityCheckAgent";
    }

    @Override
    public AgentType getAgentType() {
        return AgentType.REACT_AGENT;
    }
}
