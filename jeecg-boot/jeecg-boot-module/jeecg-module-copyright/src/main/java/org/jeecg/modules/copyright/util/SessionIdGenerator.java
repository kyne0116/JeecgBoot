package org.jeecg.modules.copyright.util;

import cn.hutool.crypto.digest.DigestUtil;
import lombok.extern.slf4j.Slf4j;

/**
 * 会话ID生成器
 * 生成规则: username_timestamp_hash8
 *
 * 示例: zhangsan_1701590400000_a1b2c3d4
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Slf4j
public class SessionIdGenerator {

    /**
     * 生成会话ID
     *
     * @param username 用户名
     * @return 会话ID，格式: username_timestamp_hash8
     */
    public static String generate(String username) {
        if (username == null || username.trim().isEmpty()) {
            throw new IllegalArgumentException("用户名不能为空");
        }

        // 当前时间戳(毫秒)
        long timestamp = System.currentTimeMillis();

        // 组合用户名和时间戳进行MD5加密，取前8位
        String source = username + timestamp;
        String md5Hash = DigestUtil.md5Hex(source);
        String hash8 = md5Hash.substring(0, 8);

        // 拼接最终的会话ID
        String sessionId = username + "_" + timestamp + "_" + hash8;

        log.debug("[SessionIdGenerator] 生成会话ID: {}", sessionId);

        return sessionId;
    }

    /**
     * 从会话ID中提取用户名
     *
     * @param sessionId 会话ID
     * @return 用户名
     */
    public static String extractUsername(String sessionId) {
        if (sessionId == null || !sessionId.contains("_")) {
            return null;
        }

        int firstUnderscoreIndex = sessionId.indexOf("_");
        return sessionId.substring(0, firstUnderscoreIndex);
    }

    /**
     * 从会话ID中提取时间戳
     *
     * @param sessionId 会话ID
     * @return 时间戳(毫秒)，解析失败返回null
     */
    public static Long extractTimestamp(String sessionId) {
        if (sessionId == null) {
            return null;
        }

        String[] parts = sessionId.split("_");
        if (parts.length < 2) {
            return null;
        }

        try {
            return Long.parseLong(parts[1]);
        } catch (NumberFormatException e) {
            log.warn("[SessionIdGenerator] 解析时间戳失败: {}", sessionId);
            return null;
        }
    }

    /**
     * 验证会话ID格式是否正确
     *
     * @param sessionId 会话ID
     * @return true-格式正确，false-格式错误
     */
    public static boolean validate(String sessionId) {
        if (sessionId == null || sessionId.trim().isEmpty()) {
            return false;
        }

        String[] parts = sessionId.split("_");

        // 必须有3部分: username_timestamp_hash8
        if (parts.length != 3) {
            return false;
        }

        // 验证用户名不为空
        if (parts[0].isEmpty()) {
            return false;
        }

        // 验证时间戳为数字
        try {
            Long.parseLong(parts[1]);
        } catch (NumberFormatException e) {
            return false;
        }

        // 验证hash为8位
        if (parts[2].length() != 8) {
            return false;
        }

        return true;
    }
}
