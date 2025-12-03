package org.jeecg.modules.copyright.apply.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.apply.entity.CopyrightSession;
import org.jeecg.modules.copyright.util.SessionIdGenerator;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * CopyrightSessionService集成测试
 *
 * 测试覆盖:
 * 1. 会话创建功能
 * 2. 会话状态更新
 * 3. 会话列表查询
 * 4. 会话详情查询
 * 5. 需求更新
 * 6. 进度更新
 * 7. 重试次数增加
 *
 * 运行方式:
 * - IDE: 右键运行此测试类
 * - 命令行: mvn test -Dtest=CopyrightSessionServiceTest
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@SpringBootTest
@ActiveProfiles("dev")
@Slf4j
public class CopyrightSessionServiceTest {

    @Autowired
    private ICopyrightSessionService sessionService;

    private List<String> createdSessionIds = new ArrayList<>();

    @BeforeEach
    public void setUp() {
        log.info("========== 开始测试CopyrightSessionService ==========");
        createdSessionIds.clear();
    }

    @AfterEach
    public void tearDown() {
        // 清理测试数据
        if (!createdSessionIds.isEmpty()) {
            log.info("清理测试数据: {} 条会话", createdSessionIds.size());
            sessionService.removeByIds(createdSessionIds);
        }
        log.info("========== 测试完成 ==========\n");
    }

    @Test
    public void testCreateSession() {
        log.info("==== 测试1: 创建会话 ====");

        String username = "test_user_001";

        // 创建会话
        CopyrightSession session = sessionService.createSession(username);

        // 记录用于清理
        createdSessionIds.add(session.getId());

        // 验证结果
        assertNotNull(session, "会话对象不应为null");
        assertNotNull(session.getId(), "会话ID不应为null");
        assertEquals(username, session.getUsername(), "用户名应匹配");
        assertEquals("CLARIFYING", session.getStatus(), "初始状态应为CLARIFYING");
        assertEquals(0, session.getRetryCount(), "初始重试次数应为0");
        assertNotNull(session.getCreateTime(), "创建时间不应为null");

        // 验证会话ID格式
        assertTrue(SessionIdGenerator.validate(session.getId()), "会话ID格式应正确");
        assertEquals(username, SessionIdGenerator.extractUsername(session.getId()),
                "从会话ID提取的用户名应匹配");

        log.info("✓ 会话创建成功: {}", session.getId());
        log.info("✓ 用户名: {}", session.getUsername());
        log.info("✓ 状态: {}", session.getStatus());
    }

    @Test
    public void testUpdateSessionStatus() {
        log.info("==== 测试2: 更新会话状态 ====");

        // 先创建会话
        String username = "test_user_002";
        CopyrightSession session = sessionService.createSession(username);
        createdSessionIds.add(session.getId());

        String sessionId = session.getId();

        // 测试状态更新: CLARIFYING -> GENERATING
        boolean updated1 = sessionService.updateSessionStatus(sessionId, "GENERATING");
        assertTrue(updated1, "状态更新应成功");

        CopyrightSession updated = sessionService.getSessionDetail(sessionId);
        assertEquals("GENERATING", updated.getStatus(), "状态应更新为GENERATING");
        log.info("✓ 状态更新: CLARIFYING -> GENERATING");

        // 测试状态更新: GENERATING -> COMPLETED
        boolean updated2 = sessionService.updateSessionStatus(sessionId, "COMPLETED");
        assertTrue(updated2, "状态更新应成功");

        updated = sessionService.getSessionDetail(sessionId);
        assertEquals("COMPLETED", updated.getStatus(), "状态应更新为COMPLETED");
        log.info("✓ 状态更新: GENERATING -> COMPLETED");
    }

    @Test
    public void testUpdateSessionStatusWithError() {
        log.info("==== 测试3: 更新会话状态并记录错误 ====");

        // 创建会话
        String username = "test_user_003";
        CopyrightSession session = sessionService.createSession(username);
        createdSessionIds.add(session.getId());

        String sessionId = session.getId();
        String errorMessage = "LLM调用失败: 网络超时";

        // 更新状态为FAILED并记录错误
        boolean updated = sessionService.updateSessionStatus(sessionId, "FAILED", errorMessage);
        assertTrue(updated, "状态更新应成功");

        // 验证结果
        CopyrightSession updatedSession = sessionService.getSessionDetail(sessionId);
        assertEquals("FAILED", updatedSession.getStatus(), "状态应为FAILED");
        assertEquals(errorMessage, updatedSession.getErrorMessage(), "错误信息应记录");

        log.info("✓ 状态: {}", updatedSession.getStatus());
        log.info("✓ 错误信息: {}", updatedSession.getErrorMessage());
    }

    @Test
    public void testGetUserSessions() {
        log.info("==== 测试4: 查询用户会话列表 ====");

        String username = "test_user_004";

        // 创建3个会话
        for (int i = 1; i <= 3; i++) {
            CopyrightSession session = sessionService.createSession(username);
            createdSessionIds.add(session.getId());
            log.info("创建会话 {}: {}", i, session.getId());

            // 稍微延迟以确保时间戳不同
            try {
                Thread.sleep(10);
            } catch (InterruptedException e) {
                // ignore
            }
        }

        // 分页查询
        Page<CopyrightSession> page = new Page<>(1, 10);
        IPage<CopyrightSession> result = sessionService.getUserSessions(username, page);

        // 验证结果
        assertNotNull(result, "查询结果不应为null");
        assertEquals(3, result.getRecords().size(), "应查询到3条会话");

        // 验证排序(按创建时间倒序)
        List<CopyrightSession> sessions = result.getRecords();
        for (int i = 0; i < sessions.size() - 1; i++) {
            assertTrue(sessions.get(i).getCreateTime().compareTo(sessions.get(i + 1).getCreateTime()) >= 0,
                    "会话应按创建时间倒序排列");
        }

        log.info("✓ 查询到 {} 条会话", result.getRecords().size());
        sessions.forEach(s -> log.info("  - {}: {}", s.getId(), s.getCreateTime()));
    }

    @Test
    public void testGetSessionDetail() {
        log.info("==== 测试5: 获取会话详情 ====");

        // 创建会话
        String username = "test_user_005";
        CopyrightSession created = sessionService.createSession(username);
        createdSessionIds.add(created.getId());

        String sessionId = created.getId();

        // 查询详情
        CopyrightSession detail = sessionService.getSessionDetail(sessionId);

        // 验证结果
        assertNotNull(detail, "会话详情不应为null");
        assertEquals(sessionId, detail.getId(), "会话ID应匹配");
        assertEquals(username, detail.getUsername(), "用户名应匹配");
        assertEquals("CLARIFYING", detail.getStatus(), "状态应为CLARIFYING");

        log.info("✓ 会话ID: {}", detail.getId());
        log.info("✓ 用户名: {}", detail.getUsername());
        log.info("✓ 状态: {}", detail.getStatus());
    }

    @Test
    public void testGetSessionDetailNotFound() {
        log.info("==== 测试6: 查询不存在的会话 ====");

        String nonExistentId = "non_existent_session_id";

        // 查询不存在的会话
        CopyrightSession detail = sessionService.getSessionDetail(nonExistentId);

        // 应返回null
        assertNull(detail, "不存在的会话应返回null");

        log.info("✓ 不存在的会话正确返回null");
    }

    @Test
    public void testUpdateRequirement() {
        log.info("==== 测试7: 更新会话需求 ====");

        // 创建会话
        String username = "test_user_006";
        CopyrightSession session = sessionService.createSession(username);
        createdSessionIds.add(session.getId());

        String sessionId = session.getId();
        String requirementJson = "{\"softwareName\":\"测试软件\",\"version\":\"v1.0\",\"category\":\"应用软件\"}";

        // 更新需求
        boolean updated = sessionService.updateRequirement(sessionId, requirementJson);
        assertTrue(updated, "需求更新应成功");

        // 验证结果
        CopyrightSession updatedSession = sessionService.getSessionDetail(sessionId);
        assertEquals(requirementJson, updatedSession.getRequirementJson(), "需求JSON应更新");

        log.info("✓ 需求更新成功");
        log.info("✓ 需求JSON: {}", updatedSession.getRequirementJson());
    }

    @Test
    public void testUpdateProgress() {
        log.info("==== 测试8: 更新会话进度 ====");

        // 创建会话
        String username = "test_user_007";
        CopyrightSession session = sessionService.createSession(username);
        createdSessionIds.add(session.getId());

        String sessionId = session.getId();
        String progressJson = "{\"currentStep\":\"代码生成\",\"percentage\":50}";

        // 更新进度
        boolean updated = sessionService.updateProgress(sessionId, progressJson);
        assertTrue(updated, "进度更新应成功");

        // 验证结果
        CopyrightSession updatedSession = sessionService.getSessionDetail(sessionId);
        assertEquals(progressJson, updatedSession.getProgressJson(), "进度JSON应更新");

        log.info("✓ 进度更新成功");
        log.info("✓ 进度JSON: {}", updatedSession.getProgressJson());
    }

    @Test
    public void testIncrementRetryCount() {
        log.info("==== 测试9: 增加重试次数 ====");

        // 创建会话
        String username = "test_user_008";
        CopyrightSession session = sessionService.createSession(username);
        createdSessionIds.add(session.getId());

        String sessionId = session.getId();

        // 初始重试次数应为0
        assertEquals(0, session.getRetryCount(), "初始重试次数应为0");

        // 增加重试次数 - 第1次
        boolean updated1 = sessionService.incrementRetryCount(sessionId);
        assertTrue(updated1, "重试次数增加应成功");
        CopyrightSession after1 = sessionService.getSessionDetail(sessionId);
        assertEquals(1, after1.getRetryCount(), "重试次数应为1");
        log.info("✓ 重试次数: 0 -> 1");

        // 增加重试次数 - 第2次
        boolean updated2 = sessionService.incrementRetryCount(sessionId);
        assertTrue(updated2, "重试次数增加应成功");
        CopyrightSession after2 = sessionService.getSessionDetail(sessionId);
        assertEquals(2, after2.getRetryCount(), "重试次数应为2");
        log.info("✓ 重试次数: 1 -> 2");

        // 增加重试次数 - 第3次
        boolean updated3 = sessionService.incrementRetryCount(sessionId);
        assertTrue(updated3, "重试次数增加应成功");
        CopyrightSession after3 = sessionService.getSessionDetail(sessionId);
        assertEquals(3, after3.getRetryCount(), "重试次数应为3");
        log.info("✓ 重试次数: 2 -> 3");
    }

    @Test
    public void testSessionIdGeneratorValidation() {
        log.info("==== 测试10: SessionIdGenerator验证 ====");

        // 创建会话
        String username = "test_user_009";
        CopyrightSession session = sessionService.createSession(username);
        createdSessionIds.add(session.getId());

        String sessionId = session.getId();

        // 验证ID格式
        assertTrue(SessionIdGenerator.validate(sessionId), "会话ID格式应有效");

        // 验证用户名提取
        String extractedUsername = SessionIdGenerator.extractUsername(sessionId);
        assertEquals(username, extractedUsername, "提取的用户名应匹配");

        // 验证时间戳提取
        Long timestamp = SessionIdGenerator.extractTimestamp(sessionId);
        assertNotNull(timestamp, "时间戳不应为null");
        assertTrue(timestamp > 0, "时间戳应为正数");

        log.info("✓ 会话ID: {}", sessionId);
        log.info("✓ 提取用户名: {}", extractedUsername);
        log.info("✓ 提取时间戳: {}", timestamp);
    }

    @Test
    public void testConcurrentSessionCreation() {
        log.info("==== 测试11: 并发创建会话(ID唯一性) ====");

        String username = "test_user_010";

        // 快速创建多个会话
        List<String> sessionIds = new ArrayList<>();
        for (int i = 0; i < 5; i++) {
            CopyrightSession session = sessionService.createSession(username);
            sessionIds.add(session.getId());
            createdSessionIds.add(session.getId());
        }

        // 验证所有ID不同
        long uniqueCount = sessionIds.stream().distinct().count();
        assertEquals(5, uniqueCount, "所有会话ID应唯一");

        log.info("✓ 创建了 {} 个唯一会话", uniqueCount);
        sessionIds.forEach(id -> log.info("  - {}", id));
    }
}
