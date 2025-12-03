package org.jeecg.modules.copyright.vo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

/**
 * 需求完整性检查响应对象
 * 用于requirementCheckTool工具函数的返回结果
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RequirementCheckResponse implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 是否完整(所有必填字段都已填写)
     */
    private boolean complete;

    /**
     * 完整度百分比(0-100)
     */
    private int completenessPercentage;

    /**
     * 各字段完整性详情
     * key: 字段名称, value: 是否已填写
     */
    private Map<String, Boolean> fieldCompleteness;

    /**
     * 缺失的字段列表
     */
    private List<String> missingFields;

    /**
     * 提示消息(引导用户补充信息)
     */
    private String message;

    /**
     * 下一步需要询问的字段(按优先级排序)
     */
    private List<String> nextFieldsToAsk;
}
