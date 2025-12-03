package org.jeecg.modules.copyright.agent.tools;

import cn.hutool.core.util.StrUtil;
import cn.hutool.json.JSONUtil;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.vo.RequirementCheckRequest;
import org.jeecg.modules.copyright.vo.RequirementCheckResponse;
import org.springframework.ai.chat.model.ToolContext;

import java.util.*;
import java.util.function.BiFunction;
import java.util.stream.Collectors;

/**
 * 需求完整性检查工具
 * 检查用户提供的软著申报信息是否完整(9个必填字段)
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Slf4j
public class RequirementCheckTool implements BiFunction<RequirementCheckRequest, ToolContext, RequirementCheckResponse> {

    public static final String DEFAULT_TOOL_DESCRIPTION =
            "检查软著申报需求信息是否完整,包含所有必填字段:软件名称、简称、版本号、分类、编程语言、技术架构、功能列表、创新点、申请人信息";

    @Override
    public RequirementCheckResponse apply(RequirementCheckRequest request, ToolContext context) {
        log.info("[工具函数] checkRequirementCompleteness 被调用");
        log.debug("[工具函数] 输入参数: {}", JSONUtil.toJsonStr(request));

        // 检查9个必填字段
        Map<String, Boolean> completeness = new LinkedHashMap<>();
        completeness.put("softwareName", StrUtil.isNotBlank(request.getSoftwareName()));
        completeness.put("shortName", StrUtil.isNotBlank(request.getShortName()));
        completeness.put("version", StrUtil.isNotBlank(request.getVersion()));
        completeness.put("category", StrUtil.isNotBlank(request.getCategory()));
        completeness.put("codeLanguage", StrUtil.isNotBlank(request.getCodeLanguage()));
        completeness.put("techStack", StrUtil.isNotBlank(request.getTechStack()));
        completeness.put("features", request.getFeatures() != null && request.getFeatures().size() >= 3);
        completeness.put("innovations", request.getInnovations() != null && request.getInnovations().size() >= 2);
        completeness.put("applicantName", StrUtil.isNotBlank(request.getApplicantName()));

        // 统计完整度
        long filledCount = completeness.values().stream().filter(v -> v).count();
        int totalCount = completeness.size();
        int completenessPercentage = (int) ((filledCount * 100) / totalCount);

        // 判断是否完整
        boolean allComplete = filledCount == totalCount;

        // 获取缺失字段
        List<String> missingFields = completeness.entrySet().stream()
                .filter(entry -> !entry.getValue())
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());

        // 构建提示消息
        String message = buildCheckMessage(allComplete, missingFields, completenessPercentage);

        // 确定下一步需要询问的字段(按优先级)
        List<String> nextFieldsToAsk = getNextFieldsToAsk(missingFields);

        RequirementCheckResponse response = RequirementCheckResponse.builder()
                .complete(allComplete)
                .completenessPercentage(completenessPercentage)
                .fieldCompleteness(completeness)
                .missingFields(missingFields)
                .message(message)
                .nextFieldsToAsk(nextFieldsToAsk)
                .build();

        log.info("[工具函数] checkRequirementCompleteness 执行结果: complete={}, percentage={}%",
                allComplete, completenessPercentage);

        return response;
    }

    /**
     * 构建检查消息
     */
    private String buildCheckMessage(boolean complete, List<String> missingFields, int percentage) {
        if (complete) {
            return "太好了!所有必填信息都已收集完成,完整度100%!";
        } else {
            String missing = String.join("、", translateFieldNames(missingFields));
            return String.format("当前完整度%d%%,还需要补充: %s", percentage, missing);
        }
    }

    /**
     * 确定下一步需要询问的字段(按优先级排序)
     */
    private List<String> getNextFieldsToAsk(List<String> missingFields) {
        // 定义字段询问优先级
        List<String> priorityOrder = Arrays.asList(
                "softwareName",      // 1. 软件名称(最基础)
                "version",           // 2. 版本号
                "category",          // 3. 软件分类
                "codeLanguage",      // 4. 编程语言
                "techStack",         // 5. 技术架构
                "features",          // 6. 功能列表
                "innovations",       // 7. 创新点
                "applicantName",     // 8. 申请人
                "shortName"          // 9. 简称(可最后询问)
        );

        return missingFields.stream()
                .sorted(Comparator.comparingInt(priorityOrder::indexOf))
                .limit(2)  // 每次最多询问2个字段
                .collect(Collectors.toList());
    }

    /**
     * 翻译字段名称为中文
     */
    private List<String> translateFieldNames(List<String> fieldNames) {
        Map<String, String> translations = new HashMap<>();
        translations.put("softwareName", "软件全称");
        translations.put("shortName", "软件简称");
        translations.put("version", "版本号");
        translations.put("category", "软件分类");
        translations.put("codeLanguage", "编程语言");
        translations.put("techStack", "技术架构");
        translations.put("features", "核心功能列表(至少3个)");
        translations.put("innovations", "技术创新点(至少2个)");
        translations.put("applicantName", "申请人信息");

        return fieldNames.stream()
                .map(field -> translations.getOrDefault(field, field))
                .collect(Collectors.toList());
    }
}
