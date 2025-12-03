package org.jeecg.modules.copyright.agent.tools;

import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.vo.CodeQualityReport;
import org.jeecg.modules.copyright.vo.GeneratedCode;
import org.springframework.ai.chat.model.ToolContext;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.BiFunction;
import java.util.regex.Pattern;

/**
 * 代码质量检查工具
 * <p>
 * 功能:
 * 1. 统计代码总行数和有效行数
 * 2. 检查代码结构完整性(实体、DAO、Service、Controller)
 * 3. 验证代码行数是否符合5000-6000行要求
 * 4. 生成质量报告和优化建议
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Component
@Slf4j
public class CodeQualityChecker implements BiFunction<GeneratedCode, ToolContext, CodeQualityReport> {

    private static final int MIN_REQUIRED_LINES = 5000;
    private static final int MAX_REQUIRED_LINES = 6000;

    // 注释行模式
    private static final Pattern COMMENT_LINE_PATTERN = Pattern.compile("^\\s*(//|/\\*|\\*|\\*/).*$");
    // 空行模式
    private static final Pattern EMPTY_LINE_PATTERN = Pattern.compile("^\\s*$");

    @Override
    public CodeQualityReport apply(GeneratedCode generatedCode, ToolContext context) {
        log.info("[CodeQualityChecker] 开始检查代码质量, 文件数量: {}",
                generatedCode.getSourceFiles().size());

        try {
            Map<String, String> sourceFiles = generatedCode.getSourceFiles();

            // 1. 统计代码行数
            int totalLines = 0;
            int effectiveLines = 0;

            for (Map.Entry<String, String> entry : sourceFiles.entrySet()) {
                String content = entry.getValue();
                String[] lines = content.split("\n");

                totalLines += lines.length;

                // 统计有效行数(去除空行和纯注释行)
                for (String line : lines) {
                    if (!EMPTY_LINE_PATTERN.matcher(line).matches()
                        && !COMMENT_LINE_PATTERN.matcher(line).matches()) {
                        effectiveLines++;
                    }
                }
            }

            // 2. 检查代码结构完整性
            boolean structureComplete = checkStructureCompleteness(sourceFiles);

            // 3. 检查是否符合行数要求
            boolean meetsRequirement = effectiveLines >= MIN_REQUIRED_LINES
                    && effectiveLines <= MAX_REQUIRED_LINES;

            // 4. 收集质量问题
            List<CodeQualityReport.QualityIssue> issues = new ArrayList<>();
            List<String> suggestions = new ArrayList<>();

            if (!meetsRequirement) {
                if (effectiveLines < MIN_REQUIRED_LINES) {
                    issues.add(CodeQualityReport.QualityIssue.builder()
                            .issueType("line_count")
                            .description(String.format("代码行数不足: 当前%d行, 需要%d-%d行",
                                    effectiveLines, MIN_REQUIRED_LINES, MAX_REQUIRED_LINES))
                            .severity("high")
                            .build());
                    suggestions.add("建议增加功能模块或完善现有代码");
                } else {
                    issues.add(CodeQualityReport.QualityIssue.builder()
                            .issueType("line_count")
                            .description(String.format("代码行数超标: 当前%d行, 需要%d-%d行",
                                    effectiveLines, MIN_REQUIRED_LINES, MAX_REQUIRED_LINES))
                            .severity("medium")
                            .build());
                    suggestions.add("建议精简冗余代码或拆分功能模块");
                }
            }

            if (!structureComplete) {
                issues.add(CodeQualityReport.QualityIssue.builder()
                        .issueType("structure")
                        .description("代码结构不完整,缺少必要的层次(实体/DAO/Service/Controller)")
                        .severity("high")
                        .build());
                suggestions.add("建议补充缺失的代码层次,确保MVC架构完整");
            }

            // 5. 构建质量报告
            CodeQualityReport report = CodeQualityReport.builder()
                    .totalLines(totalLines)
                    .effectiveLines(effectiveLines)
                    .meetsRequirement(meetsRequirement)
                    .structureComplete(structureComplete)
                    .issues(issues)
                    .suggestions(suggestions)
                    .build();

            log.info("[CodeQualityChecker] 质量检查完成 - 总行数:{}, 有效行数:{}, 符合要求:{}",
                    totalLines, effectiveLines, meetsRequirement);

            return report;

        } catch (Exception e) {
            log.error("[CodeQualityChecker] 质量检查失败", e);

            // 返回失败报告
            return CodeQualityReport.builder()
                    .totalLines(0)
                    .effectiveLines(0)
                    .meetsRequirement(false)
                    .structureComplete(false)
                    .issues(List.of(CodeQualityReport.QualityIssue.builder()
                            .issueType("error")
                            .description("质量检查失败: " + e.getMessage())
                            .severity("high")
                            .build()))
                    .suggestions(List.of("请重新生成代码"))
                    .build();
        }
    }

    /**
     * 检查代码结构完整性
     */
    private boolean checkStructureCompleteness(Map<String, String> sourceFiles) {
        boolean hasEntity = false;
        boolean hasDao = false;
        boolean hasService = false;
        boolean hasController = false;

        for (String filePath : sourceFiles.keySet()) {
            String lowerPath = filePath.toLowerCase();

            if (lowerPath.contains("/entity/") || lowerPath.contains("\\entity\\")) {
                hasEntity = true;
            }
            if (lowerPath.contains("/mapper/") || lowerPath.contains("\\mapper\\")
                    || lowerPath.contains("/dao/") || lowerPath.contains("\\dao\\")) {
                hasDao = true;
            }
            if (lowerPath.contains("/service/") || lowerPath.contains("\\service\\")) {
                hasService = true;
            }
            if (lowerPath.contains("/controller/") || lowerPath.contains("\\controller\\")) {
                hasController = true;
            }
        }

        log.debug("[CodeQualityChecker] 结构检查 - Entity:{}, DAO:{}, Service:{}, Controller:{}",
                hasEntity, hasDao, hasService, hasController);

        // 至少需要包含3个层次
        int layerCount = (hasEntity ? 1 : 0) + (hasDao ? 1 : 0)
                + (hasService ? 1 : 0) + (hasController ? 1 : 0);

        return layerCount >= 3;
    }
}
