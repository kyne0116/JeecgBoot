package org.jeecg.modules.copyright.agent.core;

/**
 * 软著申报Agent基础接口
 * 所有Agent(ReactClarifyAgent、ReactCodeGenAgent等)都需要实现此接口
 *
 * @author Claude Code
 * @since 2025-12-02
 */
public interface CopyrightAgent {

    /**
     * 执行Agent任务
     *
     * @param context Agent执行上下文
     * @return Agent执行结果
     */
    AgentResult execute(AgentContext context);

    /**
     * 获取Agent名称
     * 例如: "ReactClarifyAgent"、"ReactCodeGenAgent"
     *
     * @return Agent名称
     */
    String getAgentName();

    /**
     * 获取Agent类型
     *
     * @return Agent类型枚举
     */
    AgentType getAgentType();

    /**
     * 获取Agent描述信息
     *
     * @return Agent描述
     */
    default String getDescription() {
        return "软著申报AI Agent";
    }

    /**
     * Agent是否需要异步执行
     * 默认false,如果需要异步执行则返回true
     *
     * @return 是否异步执行
     */
    default boolean isAsync() {
        return false;
    }
}
