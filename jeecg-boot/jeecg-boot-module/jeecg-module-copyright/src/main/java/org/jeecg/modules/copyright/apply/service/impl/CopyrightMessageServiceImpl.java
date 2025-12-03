package org.jeecg.modules.copyright.apply.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.common.util.oConvertUtils;
import org.jeecg.modules.copyright.apply.entity.CopyrightMessage;
import org.jeecg.modules.copyright.apply.mapper.CopyrightMessageMapper;
import org.jeecg.modules.copyright.apply.service.ICopyrightMessageService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

/**
 * @Description: 软著申请聊天记录服务实现
 * @Author: jeecg-boot
 * @Date: 2025-12-02
 * @Version: V1.0
 */
@Service
@Slf4j
public class CopyrightMessageServiceImpl extends ServiceImpl<CopyrightMessageMapper, CopyrightMessage> implements ICopyrightMessageService {

    @Override
    @Transactional(rollbackFor = Exception.class)
    public CopyrightMessage saveMessage(String sessionId, String role, String content) {
        return saveMessage(sessionId, role, content, "text", null);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public CopyrightMessage saveMessage(String sessionId, String role, String content, String agentName) {
        return saveMessage(sessionId, role, content, "text", agentName);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public CopyrightMessage saveMessage(String sessionId, String role, String content, String messageType, String agentName) {
        log.debug("[CopyrightMessageService] 保存消息, sessionId: {}, role: {}, type: {}",
                sessionId, role, messageType);

        // 获取下一个序号
        int sequenceNo = getNextSequenceNo(sessionId);

        // 创建消息对象
        CopyrightMessage message = new CopyrightMessage();
        message.setSessionId(sessionId);
        message.setRole(role);
        message.setContent(content);
        message.setMessageType(oConvertUtils.isEmpty(messageType) ? "text" : messageType);
        message.setSequenceNo(sequenceNo);
        message.setCreateTime(new Date());
        message.setDelFlag(0);

        if (oConvertUtils.isNotEmpty(agentName)) {
            message.setAgentName(agentName);
        }

        // 保存到数据库
        boolean saved = this.save(message);
        if (!saved) {
            log.error("[CopyrightMessageService] 消息保存失败, sessionId: {}, sequenceNo: {}",
                    sessionId, sequenceNo);
            throw new RuntimeException("消息保存失败");
        }

        log.debug("[CopyrightMessageService] 消息保存成功, id: {}, sequenceNo: {}",
                message.getId(), sequenceNo);

        return message;
    }

    @Override
    public IPage<CopyrightMessage> getSessionMessages(String sessionId, Page<CopyrightMessage> page) {
        log.info("[CopyrightMessageService] 查询会话消息(分页), sessionId: {}, page: {}/{}",
                sessionId, page.getCurrent(), page.getSize());

        LambdaQueryWrapper<CopyrightMessage> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(CopyrightMessage::getSessionId, sessionId);
        queryWrapper.eq(CopyrightMessage::getDelFlag, 0);
        queryWrapper.orderByAsc(CopyrightMessage::getSequenceNo); // 按序号升序

        IPage<CopyrightMessage> result = this.page(page, queryWrapper);

        log.info("[CopyrightMessageService] 查询到 {} 条消息", result.getRecords().size());
        return result;
    }

    @Override
    public List<CopyrightMessage> getSessionMessages(String sessionId) {
        log.info("[CopyrightMessageService] 查询会话所有消息, sessionId: {}", sessionId);

        LambdaQueryWrapper<CopyrightMessage> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(CopyrightMessage::getSessionId, sessionId);
        queryWrapper.eq(CopyrightMessage::getDelFlag, 0);
        queryWrapper.orderByAsc(CopyrightMessage::getSequenceNo);

        List<CopyrightMessage> messages = this.list(queryWrapper);

        log.info("[CopyrightMessageService] 查询到 {} 条消息", messages.size());
        return messages;
    }

    @Override
    public List<CopyrightMessage> getRecentMessages(String sessionId, int limit) {
        log.debug("[CopyrightMessageService] 查询最近消息, sessionId: {}, limit: {}", sessionId, limit);

        LambdaQueryWrapper<CopyrightMessage> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(CopyrightMessage::getSessionId, sessionId);
        queryWrapper.eq(CopyrightMessage::getDelFlag, 0);
        queryWrapper.orderByDesc(CopyrightMessage::getSequenceNo); // 按序号降序
        queryWrapper.last("LIMIT " + limit); // 限制数量

        List<CopyrightMessage> messages = this.list(queryWrapper);

        log.debug("[CopyrightMessageService] 查询到 {} 条最近消息", messages.size());
        return messages;
    }

    @Override
    public String buildDialogueContext(String sessionId, int limit) {
        log.debug("[CopyrightMessageService] 构建对话上下文, sessionId: {}, limit: {}", sessionId, limit);

        // 获取最近N条消息
        List<CopyrightMessage> recentMessages = getRecentMessages(sessionId, limit);

        // 反转列表使其按时间顺序(从旧到新)
        java.util.Collections.reverse(recentMessages);

        // 构建对话上下文
        StringBuilder context = new StringBuilder();
        context.append("=== 对话历史 ===\n");

        for (CopyrightMessage message : recentMessages) {
            String roleLabel = getRoleLabel(message.getRole());

            if (oConvertUtils.isNotEmpty(message.getAgentName())) {
                context.append(String.format("%s [%s]: %s\n",
                        roleLabel, message.getAgentName(), message.getContent()));
            } else {
                context.append(String.format("%s: %s\n",
                        roleLabel, message.getContent()));
            }
        }

        context.append("=== 对话历史结束 ===\n");

        String result = context.toString();
        log.debug("[CopyrightMessageService] 对话上下文构建完成, 包含 {} 条消息", recentMessages.size());

        return result;
    }

    @Override
    public int getNextSequenceNo(String sessionId) {
        LambdaQueryWrapper<CopyrightMessage> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(CopyrightMessage::getSessionId, sessionId);
        queryWrapper.eq(CopyrightMessage::getDelFlag, 0);
        queryWrapper.orderByDesc(CopyrightMessage::getSequenceNo);
        queryWrapper.last("LIMIT 1");

        CopyrightMessage lastMessage = this.getOne(queryWrapper);

        if (lastMessage == null) {
            return 1; // 第一条消息
        }

        return lastMessage.getSequenceNo() + 1;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public int deleteSessionMessages(String sessionId) {
        log.info("[CopyrightMessageService] 删除会话消息, sessionId: {}", sessionId);

        LambdaQueryWrapper<CopyrightMessage> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(CopyrightMessage::getSessionId, sessionId);

        List<CopyrightMessage> messages = this.list(queryWrapper);
        int count = messages.size();

        if (count > 0) {
            List<String> ids = messages.stream()
                    .map(CopyrightMessage::getId)
                    .collect(Collectors.toList());
            this.removeByIds(ids);
        }

        log.info("[CopyrightMessageService] 删除了 {} 条消息", count);
        return count;
    }

    /**
     * 获取角色标签
     *
     * @param role 角色
     * @return 中文标签
     */
    private String getRoleLabel(String role) {
        if (role == null) {
            return "未知";
        }
        switch (role.toLowerCase()) {
            case "user":
                return "用户";
            case "assistant":
                return "助手";
            case "system":
                return "系统";
            default:
                return role;
        }
    }
}
