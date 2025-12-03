package org.jeecg.modules.copyright.agent.core;

import cn.hutool.core.exceptions.ExceptionUtil;
import cn.hutool.json.JSONUtil;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.jeecg.modules.copyright.agent.event.AgentEventPublisher;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.lang.reflect.Method;

/**
 * Agent执行日志AOP切面
 * 拦截标注了@LogAgentExecution的Agent execute方法,
 * 自动记录执行日志、发布事件、统计执行时长
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Aspect
@Component
@Slf4j
public class AgentExecutionAspect {

    @Autowired
    private AgentEventPublisher eventPublisher;

    /**
     * 环绕通知: 拦截Agent执行方法
     */
    @Around("@annotation(org.jeecg.modules.copyright.agent.core.LogAgentExecution)")
    public Object logAgentExecution(ProceedingJoinPoint joinPoint) throws Throwable {
        // 获取Agent实例
        Object target = joinPoint.getTarget();
        String agentName = target.getClass().getSimpleName();

        // 获取方法签名和注解
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        Method method = signature.getMethod();
        LogAgentExecution annotation = method.getAnnotation(LogAgentExecution.class);

        // 获取AgentContext参数
        Object[] args = joinPoint.getArgs();
        String sessionId = null;
        String userId = null;
        AgentContext context = null;

        if (args.length > 0 && args[0] instanceof AgentContext) {
            context = (AgentContext) args[0];
            sessionId = context.getSessionId();
            userId = context.getUserId();
        }

        // 记录开始时间
        long startTime = System.currentTimeMillis();

        // 记录Agent启动日志
        log.info("═══════════════════════════════════════════════════");
        log.info("[Agent执行开始] Agent: {}", agentName);
        log.info("[Agent执行开始] 会话ID: {}", sessionId);
        log.info("[Agent执行开始] 用户ID: {}", userId);

        if (annotation.logInput() && context != null) {
            log.info("[Agent执行开始] 输入参数: {}",
                    JSONUtil.toJsonStr(context.getRequirement()));
        }

        // 发布Agent启动事件
        if (annotation.publishEvent() && sessionId != null) {
            eventPublisher.publishAgentStarted(sessionId, agentName);
        }

        // 执行Agent方法
        AgentResult result = null;
        boolean success = false;

        try {
            result = (AgentResult) joinPoint.proceed();
            success = result != null && result.isSuccess();

            // 记录执行结果
            long duration = System.currentTimeMillis() - startTime;

            log.info("───────────────────────────────────────────────────");
            log.info("[Agent执行完成] Agent: {}", agentName);
            log.info("[Agent执行完成] 会话ID: {}", sessionId);
            log.info("[Agent执行完成] 执行时长: {}ms", duration);
            log.info("[Agent执行完成] 执行状态: {}", success ? "成功" : "失败");
            log.info("[Agent执行完成] 结果消息: {}", result.getMessage());

            if (annotation.logOutput() && result.getData() != null) {
                log.info("[Agent执行完成] 输出数据: {}",
                        JSONUtil.toJsonStr(result.getData()));
            }

            if (!result.getGeneratedFiles().isEmpty()) {
                log.info("[Agent执行完成] 生成文件: {}",
                        String.join(", ", result.getGeneratedFiles()));
            }

            log.info("═══════════════════════════════════════════════════");

            // 发布Agent完成事件
            if (annotation.publishEvent() && sessionId != null) {
                if (success) {
                    eventPublisher.publishAgentCompleted(sessionId, agentName, result, duration);
                } else {
                    eventPublisher.publishAgentFailed(sessionId, agentName, result, duration);
                }
            }

            return result;

        } catch (Exception e) {
            // 捕获异常并记录
            long duration = System.currentTimeMillis() - startTime;

            log.error("═══════════════════════════════════════════════════");
            log.error("[Agent执行异常] Agent: {}", agentName);
            log.error("[Agent执行异常] 会话ID: {}", sessionId);
            log.error("[Agent执行异常] 执行时长: {}ms", duration);
            log.error("[Agent执行异常] 异常信息: {}", e.getMessage(), e);
            log.error("═══════════════════════════════════════════════════");

            // 构建失败结果
            result = AgentResult.failure(
                    "Agent执行异常: " + e.getMessage(),
                    ExceptionUtil.stacktraceToString(e)
            );

            // 发布Agent失败事件
            if (annotation.publishEvent() && sessionId != null) {
                eventPublisher.publishAgentFailed(sessionId, agentName, result, duration);
            }

            throw e;
        }
    }
}
