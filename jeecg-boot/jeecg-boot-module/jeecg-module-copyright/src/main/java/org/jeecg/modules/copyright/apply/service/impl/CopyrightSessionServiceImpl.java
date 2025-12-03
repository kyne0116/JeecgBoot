package org.jeecg.modules.copyright.apply.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.common.util.oConvertUtils;
import org.jeecg.modules.copyright.apply.entity.CopyrightSession;
import org.jeecg.modules.copyright.apply.mapper.CopyrightSessionMapper;
import org.jeecg.modules.copyright.apply.service.ICopyrightSessionService;
import org.jeecg.modules.copyright.util.SessionIdGenerator;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;

/**
 * @Description: 软著申请会话服务实现
 * @Author: jeecg-boot
 * @Date: 2025-12-02
 * @Version: V1.0
 */
@Service
@Slf4j
public class CopyrightSessionServiceImpl extends ServiceImpl<CopyrightSessionMapper, CopyrightSession> implements ICopyrightSessionService {

    @Override
    @Transactional(rollbackFor = Exception.class)
    public CopyrightSession createSession(String username) {
        log.info("[CopyrightSessionService] 创建新会话, 用户: {}", username);

        // 生成会话ID
        String sessionId = SessionIdGenerator.generate(username);

        // 创建会话对象
        CopyrightSession session = new CopyrightSession();
        session.setId(sessionId);
        session.setUsername(username);
        session.setStatus("CLARIFYING"); // 初始状态：需求澄清中
        session.setCreateTime(new Date());
        session.setRetryCount(0);
        session.setDelFlag(0);

        // 保存到数据库
        boolean saved = this.save(session);
        if (!saved) {
            log.error("[CopyrightSessionService] 会话创建失败, sessionId: {}", sessionId);
            throw new RuntimeException("会话创建失败");
        }

        log.info("[CopyrightSessionService] 会话创建成功, sessionId: {}", sessionId);
        return session;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateSessionStatus(String sessionId, String status) {
        return updateSessionStatus(sessionId, status, null);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateSessionStatus(String sessionId, String status, String errorMessage) {
        log.info("[CopyrightSessionService] 更新会话状态, sessionId: {}, status: {}", sessionId, status);

        CopyrightSession session = new CopyrightSession();
        session.setId(sessionId);
        session.setStatus(status);
        session.setUpdateTime(new Date());

        if (oConvertUtils.isNotEmpty(errorMessage)) {
            session.setErrorMessage(errorMessage);
        }

        boolean updated = this.updateById(session);
        if (!updated) {
            log.warn("[CopyrightSessionService] 会话状态更新失败, sessionId: {}", sessionId);
        }

        return updated;
    }

    @Override
    public IPage<CopyrightSession> getUserSessions(String username, Page<CopyrightSession> page) {
        log.info("[CopyrightSessionService] 查询用户会话列表, username: {}, page: {}/{}",
                username, page.getCurrent(), page.getSize());

        LambdaQueryWrapper<CopyrightSession> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(CopyrightSession::getUsername, username);
        queryWrapper.eq(CopyrightSession::getDelFlag, 0); // 未删除
        queryWrapper.orderByDesc(CopyrightSession::getCreateTime); // 按创建时间倒序

        IPage<CopyrightSession> result = this.page(page, queryWrapper);

        log.info("[CopyrightSessionService] 查询到{}条会话记录", result.getRecords().size());
        return result;
    }

    @Override
    public CopyrightSession getSessionDetail(String sessionId) {
        log.info("[CopyrightSessionService] 查询会话详情, sessionId: {}", sessionId);

        CopyrightSession session = this.getById(sessionId);

        if (session == null) {
            log.warn("[CopyrightSessionService] 会话不存在, sessionId: {}", sessionId);
        } else if (session.getDelFlag() != null && session.getDelFlag() == 1) {
            log.warn("[CopyrightSessionService] 会话已删除, sessionId: {}", sessionId);
            return null;
        }

        return session;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateRequirement(String sessionId, String requirementJson) {
        log.info("[CopyrightSessionService] 更新会话需求, sessionId: {}", sessionId);

        CopyrightSession session = new CopyrightSession();
        session.setId(sessionId);
        session.setRequirementJson(requirementJson);
        session.setUpdateTime(new Date());

        return this.updateById(session);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateProgress(String sessionId, String progressJson) {
        log.debug("[CopyrightSessionService] 更新会话进度, sessionId: {}", sessionId);

        CopyrightSession session = new CopyrightSession();
        session.setId(sessionId);
        session.setProgressJson(progressJson);
        session.setUpdateTime(new Date());

        return this.updateById(session);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean incrementRetryCount(String sessionId) {
        log.info("[CopyrightSessionService] 增加重试次数, sessionId: {}", sessionId);

        // 先查询当前重试次数
        CopyrightSession current = this.getById(sessionId);
        if (current == null) {
            log.warn("[CopyrightSessionService] 会话不存在, sessionId: {}", sessionId);
            return false;
        }

        int currentRetryCount = current.getRetryCount() == null ? 0 : current.getRetryCount();
        int newRetryCount = currentRetryCount + 1;

        CopyrightSession session = new CopyrightSession();
        session.setId(sessionId);
        session.setRetryCount(newRetryCount);
        session.setUpdateTime(new Date());

        log.info("[CopyrightSessionService] 重试次数: {} -> {}", currentRetryCount, newRetryCount);

        return this.updateById(session);
    }
}

