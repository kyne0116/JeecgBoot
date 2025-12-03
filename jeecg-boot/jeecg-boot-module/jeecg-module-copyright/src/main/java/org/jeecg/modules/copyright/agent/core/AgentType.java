package org.jeecg.modules.copyright.agent.core;

/**
 * Agent类型枚举
 *
 * @author Claude Code
 * @since 2025-12-02
 */
public enum AgentType {

    /**
     * ReactAgent: 推理-行动Agent,支持工具调用和多轮推理
     */
    REACT_AGENT("ReactAgent", "推理-行动Agent"),

    /**
     * 普通Agent: 基于ChatClient的简单Agent,不支持自主推理
     */
    SIMPLE_AGENT("SimpleAgent", "简单Agent");

    private final String code;
    private final String description;

    AgentType(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }
}
