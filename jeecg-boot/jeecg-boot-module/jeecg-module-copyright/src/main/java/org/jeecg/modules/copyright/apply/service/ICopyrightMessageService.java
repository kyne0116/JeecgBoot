package org.jeecg.modules.copyright.apply.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import org.jeecg.modules.copyright.apply.entity.CopyrightMessage;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;

/**
 * @Description: 软著申请聊天记录服务接口
 * @Author: jeecg-boot
 * @Date:   2025-12-02
 * @Version: V1.0
 */
public interface ICopyrightMessageService extends IService<CopyrightMessage> {

    /**
     * 保存对话消息
     *
     * @param sessionId   会话ID
     * @param role        角色(user/assistant/system)
     * @param content     消息内容
     * @return 保存的消息对象
     */
    CopyrightMessage saveMessage(String sessionId, String role, String content);

    /**
     * 保存对话消息(带Agent名称)
     *
     * @param sessionId   会话ID
     * @param role        角色(user/assistant/system)
     * @param content     消息内容
     * @param agentName   Agent名称
     * @return 保存的消息对象
     */
    CopyrightMessage saveMessage(String sessionId, String role, String content, String agentName);

    /**
     * 保存对话消息(完整参数)
     *
     * @param sessionId    会话ID
     * @param role         角色
     * @param content      消息内容
     * @param messageType  消息类型(text/status/progress/error)
     * @param agentName    Agent名称
     * @return 保存的消息对象
     */
    CopyrightMessage saveMessage(String sessionId, String role, String content, String messageType, String agentName);

    /**
     * 获取会话的消息历史(分页)
     *
     * @param sessionId 会话ID
     * @param page      分页对象
     * @return 分页结果
     */
    IPage<CopyrightMessage> getSessionMessages(String sessionId, Page<CopyrightMessage> page);

    /**
     * 获取会话的消息历史(全部)
     *
     * @param sessionId 会话ID
     * @return 消息列表，按sequenceNo升序
     */
    List<CopyrightMessage> getSessionMessages(String sessionId);

    /**
     * 获取会话的最近N条消息
     *
     * @param sessionId 会话ID
     * @param limit     数量限制
     * @return 消息列表，按sequenceNo降序
     */
    List<CopyrightMessage> getRecentMessages(String sessionId, int limit);

    /**
     * 构建对话上下文(供LLM使用)
     *
     * @param sessionId 会话ID
     * @param limit     最多包含多少条历史消息
     * @return 格式化的对话上下文字符串
     */
    String buildDialogueContext(String sessionId, int limit);

    /**
     * 获取会话的下一个消息序号
     *
     * @param sessionId 会话ID
     * @return 下一个序号
     */
    int getNextSequenceNo(String sessionId);

    /**
     * 删除会话的所有消息
     *
     * @param sessionId 会话ID
     * @return 删除的消息数量
     */
    int deleteSessionMessages(String sessionId);
}
