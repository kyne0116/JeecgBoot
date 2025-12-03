package org.jeecg.modules.copyright.sse.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.common.api.vo.Result;
import org.jeecg.common.aspect.annotation.PermissionData;
import org.jeecg.modules.copyright.agent.service.ReactClarifyAgentSSEService;
import org.jeecg.modules.copyright.apply.entity.CopyrightSession;
import org.jeecg.modules.copyright.apply.service.ICopyrightSessionService;
import org.jeecg.modules.copyright.sse.manager.SseEmitterManager;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

/**
 * 软著SSE API控制器
 *
 * 提供前端Vue3应用所需的SSE相关API端点
 *
 * @author Claude Code
 * @since 2025-12-03 (前后端联调)
 */
@Tag(name = "软著SSE API")
@RestController
@RequestMapping("/copyright/sse")
@Slf4j
public class CopyrightSSEApiController {

    @Autowired
    private ICopyrightSessionService sessionService;

    @Autowired
    private ReactClarifyAgentSSEService clarifyAgentService;

    @Autowired
    private SseEmitterManager emitterManager;

    /**
     * 创建新会话
     *
     * @param userId 用户ID
     * @param username 用户名
     * @param initialRequirement 初始需求描述
     * @return 会话信息
     */
    @Operation(summary = "创建新会话")
    @PostMapping("/session/create")
    @PermissionData(pageComponent = "copyright/CopyrightChatApp")
    public Result<CopyrightSession> createSession(
            @RequestParam(required = false) String userId,
            @RequestParam(required = false) String username,
            @RequestParam String initialRequirement) {

        log.info("[CopyrightSSEApiController] 创建新会话, user: {}, requirement: {}",
                username, initialRequirement);

        try {
            // 1. 创建会话记录
            CopyrightSession session = sessionService.createSession(username != null ? username : userId);

            // 2. 异步启动需求澄清流程
            clarifyAgentService.startClarification(session.getId(),
                    username != null ? username : userId,
                    initialRequirement);

            log.info("[CopyrightSSEApiController] 会话创建成功, sessionId: {}", session.getId());
            return Result.OK(session);

        } catch (Exception e) {
            log.error("[CopyrightSSEApiController] 创建会话失败", e);
            return Result.error("创建会话失败: " + e.getMessage());
        }
    }

    /**
     * 获取会话详情
     *
     * @param sessionId 会话ID
     * @return 会话信息
     */
    @Operation(summary = "获取会话详情")
    @GetMapping("/session/{sessionId}")
    @PermissionData(pageComponent = "copyright/CopyrightChatApp")
    public Result<CopyrightSession> getSession(@PathVariable String sessionId) {
        log.info("[CopyrightSSEApiController] 查询会话, sessionId: {}", sessionId);

        try {
            CopyrightSession session = sessionService.getById(sessionId);
            if (session == null) {
                return Result.error("会话不存在: " + sessionId);
            }
            return Result.OK(session);

        } catch (Exception e) {
            log.error("[CopyrightSSEApiController] 查询会话失败", e);
            return Result.error("查询会话失败: " + e.getMessage());
        }
    }

    /**
     * 发送用户输入
     *
     * @param sessionId 会话ID
     * @param userInput 用户输入内容
     * @return 成功或失败
     */
    @Operation(summary = "发送用户输入")
    @PostMapping("/user-input")
    @PermissionData(pageComponent = "copyright/CopyrightChatApp")
    public Result<Void> sendUserInput(
            @RequestParam String sessionId,
            @RequestParam String userInput) {

        log.info("[CopyrightSSEApiController] 收到用户输入, sessionId: {}, input: {}",
                sessionId, userInput);

        try {
            // 将用户输入推送到队列，Agent将从队列中获取
            clarifyAgentService.submitUserInput(sessionId, userInput);
            return Result.OK("用户输入已接收");

        } catch (Exception e) {
            log.error("[CopyrightSSEApiController] 发送用户输入失败", e);
            return Result.error("发送用户输入失败: " + e.getMessage());
        }
    }

    /**
     * 建立SSE连接
     *
     * @param sessionId 会话ID
     * @return SseEmitter对象
     */
    @Operation(summary = "建立SSE连接")
    @GetMapping(value = "/connect/{sessionId}", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    @PermissionData(pageComponent = "copyright/CopyrightChatApp")
    public SseEmitter connect(@PathVariable String sessionId) {
        log.info("[CopyrightSSEApiController] 建立SSE连接, sessionId: {}", sessionId);

        try {
            // 创建并注册SseEmitter
            SseEmitter emitter = emitterManager.createEmitter(sessionId);

            // 发送连接成功消息
            emitterManager.sendStatus(sessionId, "SSE连接已建立");

            log.info("[CopyrightSSEApiController] SSE连接创建成功, sessionId: {}", sessionId);
            return emitter;

        } catch (Exception e) {
            log.error("[CopyrightSSEApiController] 建立SSE连接失败", e);
            throw new RuntimeException("建立SSE连接失败: " + e.getMessage());
        }
    }
}
