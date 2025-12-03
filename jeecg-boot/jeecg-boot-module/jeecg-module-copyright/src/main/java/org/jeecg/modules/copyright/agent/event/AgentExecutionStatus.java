package org.jeecg.modules.copyright.agent.event;

/**
 * Agent执行状态枚举
 *
 * @author Claude Code
 * @since 2025-12-02
 */
public enum AgentExecutionStatus {

    /**
     * 已启动
     */
    STARTED("started", "已启动"),

    /**
     * 执行中
     */
    RUNNING("running", "执行中"),

    /**
     * 已完成
     */
    COMPLETED("completed", "已完成"),

    /**
     * 执行失败
     */
    FAILED("failed", "执行失败");

    private final String code;
    private final String description;

    AgentExecutionStatus(String code, String description) {
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
