package org.jeecg.modules.copyright.agent.core;

import java.lang.annotation.*;

/**
 * Agent执行日志注解
 * 标注在Agent的execute方法上,自动记录执行日志
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface LogAgentExecution {

    /**
     * 是否记录输入参数
     */
    boolean logInput() default true;

    /**
     * 是否记录输出结果
     */
    boolean logOutput() default true;

    /**
     * 是否发布Agent事件
     */
    boolean publishEvent() default true;
}
