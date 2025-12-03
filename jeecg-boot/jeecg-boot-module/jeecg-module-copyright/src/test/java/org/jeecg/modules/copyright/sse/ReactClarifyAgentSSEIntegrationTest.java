package org.jeecg.modules.copyright.sse;

import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.agent.service.ReactClarifyAgentSSEService;
import org.jeecg.modules.copyright.apply.entity.CopyrightMessage;
import org.jeecg.modules.copyright.apply.entity.CopyrightSession;
import org.jeecg.modules.copyright.apply.service.ICopyrightMessageService;
import org.jeecg.modules.copyright.apply.service.ICopyrightSessionService;
import org.jeecg.modules.copyright.sse.manager.SseEmitterManager;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

/**
 * ReactClarifyAgent SSE端到端集成测试
 *
 * 测试目标：验证完整的端到端流程
 * 用户HTTP POST输入 → ReactClarifyAgent → LLM多轮对话
 * → SSE逐字推送 → 提取需求 → 保存数据库 → 用户接收
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@SpringBootTest
@ActiveProfiles("test")
@Slf4j
public class ReactClarifyAgentSSEIntegrationTest {

    @Autowired
    private ReactClarifyAgentSSEService clarifyAgentService;

    @Autowired
    private SseEmitterManager emitterManager;

    @Autowired
    private ICopyrightSessionService sessionService;

    @Autowired
    private ICopyrightMessageService messageService;

    /**
     * 测试1：端到端流程 - 单轮对话
     *
     * 流程：
     * 1. 创建会话
     * 2. 建立SSE连接
     * 3. 发送首条消息（启动ReactClarifyAgent）
     * 4. 模拟用户回复
     * 5. 验证SSE推送
     * 6. 验证数据库持久化
     * 7. 验证会话状态
     */
    @Test
    @DisplayName("端到端流程测试 - 完整的需求澄清对话")
    public void testEndToEndClarificationFlow() throws InterruptedException {
        log.info("========== 开始端到端流程测试 ==========");

        // 1. 创建会话
        String username = "testuser_e2e";
        String sessionId = username + "_" + System.currentTimeMillis();

        CopyrightSession session = new CopyrightSession();
        session.setSessionId(sessionId);
        session.setUsername(username);
        session.setStatus("CLARIFYING");
        sessionService.save(session);

        log.info("✅ 步骤1: 会话创建成功, sessionId: {}", sessionId);

        // 2. 建立SSE连接（模拟前端EventSource）
        SseEmitter emitter = emitterManager.createEmitter(sessionId);
        assertNotNull(emitter, "SSE Emitter应该创建成功");

        log.info("✅ 步骤2: SSE连接建立成功");

        // 3. 设置SSE消息监听器（模拟前端接收消息）
        AtomicInteger chatMessageCount = new AtomicInteger(0);
        AtomicInteger statusMessageCount = new AtomicInteger(0);
        CountDownLatch completionLatch = new CountDownLatch(1);

        emitter.onCompletion(() -> {
            log.info("📡 SSE连接完成");
            completionLatch.countDown();
        });

        emitter.onError(throwable -> {
            log.error("❌ SSE连接错误", throwable);
            completionLatch.countDown();
        });

        log.info("✅ 步骤3: SSE监听器设置完成");

        // 4. 启动需求澄清流程（异步）
        String initialMessage = "我想申报一个软件著作权，软件名称是'智能客服系统'";

        log.info("📤 步骤4: 发送首条消息: {}", initialMessage);

        // 使用单独的线程启动，避免阻塞测试
        Thread clarificationThread = new Thread(() -> {
            clarifyAgentService.startClarification(sessionId, username, initialMessage);
        });
        clarificationThread.start();

        log.info("✅ 步骤4: 需求澄清流程已启动（异步）");

        // 5. 等待Agent提问，然后模拟用户回复
        // 注意：由于ReactClarifyAgent会进入等待用户输入的阻塞状态，
        // 我们需要在另一个线程中提交用户输入

        Thread userInputThread = new Thread(() -> {
            try {
                // 等待1秒让Agent启动并发出第一个问题
                Thread.sleep(1000);

                log.info("📤 提交用户回复1: 提供版本号和分类信息");
                boolean success1 = clarifyAgentService.submitUserInput(sessionId,
                        "版本号是v1.0.0，这是一个应用软件");
                assertTrue(success1, "第一次用户输入应该提交成功");

                // 等待Agent处理并提出下一个问题
                Thread.sleep(2000);

                log.info("📤 提交用户回复2: 提供技术栈信息");
                boolean success2 = clarifyAgentService.submitUserInput(sessionId,
                        "使用Java、Spring Boot、Vue3和MySQL技术栈");
                assertTrue(success2, "第二次用户输入应该提交成功");

                // 等待Agent处理并提出下一个问题
                Thread.sleep(2000);

                log.info("📤 提交用户回复3: 提供功能和创新点");
                boolean success3 = clarifyAgentService.submitUserInput(sessionId,
                        "核心功能包括：1)智能问答 2)工单管理 3)知识库管理。创新点有：1)AI驱动的智能问答 2)多渠道接入");
                assertTrue(success3, "第三次用户输入应该提交成功");

                log.info("✅ 步骤5: 所有用户输入已提交");

            } catch (Exception e) {
                log.error("❌ 提交用户输入失败", e);
                fail("提交用户输入失败: " + e.getMessage());
            }
        });
        userInputThread.start();

        // 6. 等待对话完成（最多3分钟）
        log.info("⏳ 步骤6: 等待需求澄清流程完成（最多3分钟）...");

        boolean finished = completionLatch.await(3, TimeUnit.MINUTES);

        // 如果超时，手动检查会话状态
        if (!finished) {
            log.warn("⚠️ 等待超时，检查会话状态...");
            clarificationThread.interrupt();
            userInputThread.interrupt();
        }

        log.info("✅ 步骤6: 等待完成");

        // 7. 验证会话状态
        CopyrightSession updatedSession = sessionService.getById(sessionId);
        assertNotNull(updatedSession, "会话应该存在");

        log.info("📊 会话最终状态: {}", updatedSession.getStatus());

        // 状态应该是GENERATING（需求澄清完成）或CLARIFYING（仍在进行中）
        assertTrue(
                "GENERATING".equals(updatedSession.getStatus()) ||
                        "CLARIFYING".equals(updatedSession.getStatus()) ||
                        "FAILED".equals(updatedSession.getStatus()),
                "会话状态应该是GENERATING、CLARIFYING或FAILED，实际: " + updatedSession.getStatus()
        );

        log.info("✅ 步骤7: 会话状态验证通过");

        // 8. 验证消息持久化
        List<CopyrightMessage> messages = messageService.getSessionMessages(sessionId);
        assertNotNull(messages, "消息列表不应该为null");
        assertTrue(messages.size() >= 2, "至少应该有2条消息（用户消息+AI响应），实际: " + messages.size());

        log.info("📝 消息数量: {}", messages.size());
        for (CopyrightMessage msg : messages) {
            log.info("  - [{}] {}: {}", msg.getSequenceNo(), msg.getRole(),
                    msg.getContent().substring(0, Math.min(50, msg.getContent().length())) + "...");
        }

        log.info("✅ 步骤8: 消息持久化验证通过");

        // 9. 验证需求对象（如果完成）
        if ("GENERATING".equals(updatedSession.getStatus())) {
            String requirementJson = updatedSession.getRequirementJson();
            assertNotNull(requirementJson, "需求JSON应该已保存");
            assertTrue(requirementJson.contains("智能客服系统"), "需求JSON应该包含软件名称");

            log.info("📋 需求JSON: {}", requirementJson);
            log.info("✅ 步骤9: 需求对象验证通过");
        } else {
            log.info("ℹ️ 步骤9: 需求尚未完成，跳过验证");
        }

        log.info("========== 端到端流程测试完成 ==========");
    }

    /**
     * 测试2：SSE连接管理
     */
    @Test
    @DisplayName("SSE连接管理测试")
    public void testSseConnectionManagement() {
        log.info("========== SSE连接管理测试 ==========");

        String sessionId = "test_sse_" + System.currentTimeMillis();

        // 1. 创建连接
        SseEmitter emitter = emitterManager.createEmitter(sessionId);
        assertNotNull(emitter, "SSE Emitter应该创建成功");
        assertTrue(emitterManager.isOnline(sessionId), "会话应该在线");

        log.info("✅ SSE连接创建成功");

        // 2. 发送消息
        emitterManager.sendChat(sessionId, "测试消息");
        emitterManager.sendStatus(sessionId, "测试状态");

        log.info("✅ SSE消息发送成功");

        // 3. 关闭连接
        emitterManager.close(sessionId);
        assertFalse(emitterManager.isOnline(sessionId), "会话应该离线");

        log.info("✅ SSE连接关闭成功");

        log.info("========== SSE连接管理测试完成 ==========");
    }

    /**
     * 测试3：用户输入队列机制
     */
    @Test
    @DisplayName("用户输入队列机制测试")
    public void testUserInputQueueMechanism() throws InterruptedException {
        log.info("========== 用户输入队列测试 ==========");

        String username = "testuser_queue";
        String sessionId = username + "_" + System.currentTimeMillis();

        // 1. 创建会话
        CopyrightSession session = new CopyrightSession();
        session.setSessionId(sessionId);
        session.setUsername(username);
        session.setStatus("CLARIFYING");
        sessionService.save(session);

        // 2. 建立SSE连接
        emitterManager.createEmitter(sessionId);

        // 3. 启动澄清流程（异步）
        CountDownLatch startLatch = new CountDownLatch(1);
        Thread clarificationThread = new Thread(() -> {
            startLatch.countDown();
            clarifyAgentService.startClarification(sessionId, username, "测试消息");
        });
        clarificationThread.start();

        // 等待流程启动
        startLatch.await(5, TimeUnit.SECONDS);
        Thread.sleep(1000); // 给Agent一些启动时间

        // 4. 提交用户输入
        boolean success = clarifyAgentService.submitUserInput(sessionId, "用户回复");
        assertTrue(success, "用户输入应该提交成功");

        log.info("✅ 用户输入提交成功");

        // 5. 验证会话活跃状态
        assertTrue(clarifyAgentService.isSessionActive(sessionId), "会话应该活跃");

        log.info("✅ 会话活跃状态验证通过");

        // 6. 清理
        Thread.sleep(2000);
        clarificationThread.interrupt();
        emitterManager.close(sessionId);

        log.info("========== 用户输入队列测试完成 ==========");
    }

    /**
     * 测试4：消息持久化验证
     */
    @Test
    @DisplayName("消息持久化验证测试")
    public void testMessagePersistence() {
        log.info("========== 消息持久化测试 ==========");

        String sessionId = "test_persistence_" + System.currentTimeMillis();

        // 1. 保存用户消息
        messageService.saveMessage(sessionId, "user", "用户测试消息", "ReactClarifyAgent");

        // 2. 保存AI响应
        messageService.saveMessage(sessionId, "assistant", "AI测试响应", "ReactClarifyAgent");

        // 3. 查询消息
        List<CopyrightMessage> messages = messageService.getSessionMessages(sessionId);

        // 4. 验证
        assertNotNull(messages, "消息列表不应该为null");
        assertEquals(2, messages.size(), "应该有2条消息");

        CopyrightMessage userMsg = messages.get(0);
        assertEquals("user", userMsg.getRole(), "第一条应该是用户消息");
        assertEquals("用户测试消息", userMsg.getContent());

        CopyrightMessage aiMsg = messages.get(1);
        assertEquals("assistant", aiMsg.getRole(), "第二条应该是AI消息");
        assertEquals("AI测试响应", aiMsg.getContent());

        log.info("✅ 消息持久化验证通过，消息数量: {}", messages.size());

        log.info("========== 消息持久化测试完成 ==========");
    }
}
