package org.jeecg.modules.copyright.apply.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import org.jeecg.modules.copyright.apply.entity.CopyrightSession;

/**
 * @Description: 软著申请会话服务接口
 * @Author: jeecg-boot
 * @Date: 2025-12-02
 * @Version: V1.0
 */
public interface ICopyrightSessionService extends IService<CopyrightSession> {

    /**
     * 创建新会话
     *
     * @param username 用户名
     * @return 创建的会话对象
     */
    CopyrightSession createSession(String username);

    /**
     * 更新会话状态
     *
     * @param sessionId 会话ID
     * @param status    新状态(CLARIFYING/GENERATING/CHECKING/COMPLETED/FAILED)
     * @return 是否更新成功
     */
    boolean updateSessionStatus(String sessionId, String status);

    /**
     * 更新会话状态和错误信息
     *
     * @param sessionId    会话ID
     * @param status       新状态
     * @param errorMessage 错误信息
     * @return 是否更新成功
     */
    boolean updateSessionStatus(String sessionId, String status, String errorMessage);

    /**
     * 获取用户的会话列表（分页）
     *
     * @param username 用户名
     * @param page     分页对象
     * @return 分页结果
     */
    IPage<CopyrightSession> getUserSessions(String username, Page<CopyrightSession> page);

    /**
     * 根据ID获取会话详情
     *
     * @param sessionId 会话ID
     * @return 会话对象，不存在返回null
     */
    CopyrightSession getSessionDetail(String sessionId);

    /**
     * 更新会话的需求JSON
     *
     * @param sessionId       会话ID
     * @param requirementJson 需求JSON字符串
     * @return 是否更新成功
     */
    boolean updateRequirement(String sessionId, String requirementJson);

    /**
     * 更新会话的进度JSON
     *
     * @param sessionId    会话ID
     * @param progressJson 进度JSON字符串
     * @return 是否更新成功
     */
    boolean updateProgress(String sessionId, String progressJson);

    /**
     * 增加重试次数
     *
     * @param sessionId 会话ID
     * @return 是否更新成功
     */
    boolean incrementRetryCount(String sessionId);
}

