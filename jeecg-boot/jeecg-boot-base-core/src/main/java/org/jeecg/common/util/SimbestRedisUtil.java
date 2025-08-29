package org.jeecg.common.util;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import javax.annotation.PostConstruct;

import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Component;

import lombok.extern.slf4j.Slf4j;

/**
 * 增强型Redis工具类 - 简化版中文Key支持
 * 
 * 特性:
 * - 基于spring.application.name的自动前缀管理
 * - 包含中文的key自动Base64编码存储
 * - 支持双向转换：编码key可解码回原始中文
 * - 纯英文key保持原样，无额外开销
 *
 * @author Simbest
 * @version 2.0
 * @since 2025-08-28
 */
@Slf4j
@Component
public class SimbestRedisUtil {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    /**
     * Redis key前缀，基于spring.application.name
     */
    @Value("${spring.application.name:jeecg-boot}")
    private String applicationName;

    /**
     * 是否启用操作日志
     */
    @Value("${jeecg.redis.log.enabled:false}")
    private boolean logEnabled;

    /**
     * 是否启用性能监控
     */
    @Value("${jeecg.redis.monitor.enabled:false}")
    private boolean monitorEnabled;

    private String keyPrefix;

    @PostConstruct
    public void init() {
        this.keyPrefix = applicationName.endsWith(":") ? applicationName : applicationName + ":";
        log.info("SimbestRedisUtil初始化完成，应用: {}, key前缀: {}", applicationName, keyPrefix);
    }

    // ==================== 内部工具方法 ====================

    /**
     * 构建完整的Redis key
     */
    private String buildKey(String key) {
        if (StringUtils.isBlank(key)) {
            throw new IllegalArgumentException("Redis key不能为空");
        }
        return keyPrefix + processKey(key);
    }

    /**
     * 构建多个完整的Redis key
     */
    private Collection<String> buildKeys(Collection<String> keys) {
        if (keys == null || keys.isEmpty()) {
            return Collections.emptyList();
        }
        return keys.stream()
                .filter(StringUtils::isNotBlank)
                .map(this::buildKey)
                .collect(Collectors.toList());
    }

    /**
     * 处理key - 包含中文则Base64编码，否则保持原样
     */
    private String processKey(String key) {
        if (StringUtils.isBlank(key)) {
            return key;
        }
        return containsChinese(key) ? encodeKey(key) : key;
    }

    /**
     * 检查字符串是否包含中文字符
     */
    private boolean containsChinese(String str) {
        if (StringUtils.isBlank(str)) {
            return false;
        }
        return str.codePoints()
                .anyMatch(codePoint -> Character.UnicodeScript.of(codePoint) == Character.UnicodeScript.HAN);
    }

    /**
     * 对包含中文的key进行Base64编码
     * 格式: b64_{base64编码}
     */
    private String encodeKey(String key) {
        try {
            String base64 = Base64.getEncoder().encodeToString(key.getBytes(StandardCharsets.UTF_8));
            return "b64_" + base64;
        } catch (Exception e) {
            log.warn("Base64编码失败，使用原始key: {}", key);
            return key;
        }
    }

    /**
     * 记录操作日志和性能监控
     */
    private <T> T executeWithMonitor(String operation, String key, java.util.function.Supplier<T> supplier) {
        long startTime = System.currentTimeMillis();
        try {
            T result = supplier.get();
            if (logEnabled || monitorEnabled) {
                long cost = System.currentTimeMillis() - startTime;
                if (logEnabled) {
                    log.debug("Redis操作: {} key: {} 耗时: {}ms", operation, key, cost);
                }
                if (monitorEnabled && cost > 100) {
                    log.warn("Redis操作耗时较长: {} key: {} 耗时: {}ms", operation, key, cost);
                }
            }
            return result;
        } catch (Exception e) {
            long cost = System.currentTimeMillis() - startTime;
            log.error("Redis操作异常: {} key: {} 耗时: {}ms 错误: {}", operation, key, cost, e.getMessage(), e);
            throw new RuntimeException("Redis操作失败: " + operation, e);
        }
    }

    // ==================== Key 相关操作 ====================

    /**
     * 检查key是否存在
     */
    public Boolean hasKey(String key) {
        return executeWithMonitor("hasKey", key, () -> stringRedisTemplate.hasKey(buildKey(key)));
    }

    /**
     * 删除单个key
     */
    public Boolean delete(String key) {
        return executeWithMonitor("delete", key, () -> stringRedisTemplate.delete(buildKey(key)));
    }

    /**
     * 批量删除key
     */
    public Long delete(Collection<String> keys) {
        return executeWithMonitor("batchDelete", keys.toString(), () -> stringRedisTemplate.delete(buildKeys(keys)));
    }

    /**
     * 设置key过期时间
     */
    public Boolean expire(String key, long timeout, TimeUnit unit) {
        return executeWithMonitor("expire", key, () -> stringRedisTemplate.expire(buildKey(key), timeout, unit));
    }

    /**
     * 获取key的剩余过期时间
     */
    public Long getExpire(String key) {
        return executeWithMonitor("getExpire", key, () -> stringRedisTemplate.getExpire(buildKey(key)));
    }

    // ==================== String 相关操作 ====================

    /**
     * 设置String值
     */
    public void set(String key, String value) {
        executeWithMonitor("set", key, () -> {
            stringRedisTemplate.opsForValue().set(buildKey(key), value);
            return null;
        });
    }

    /**
     * 设置String值并指定过期时间
     */
    public void set(String key, String value, long timeout, TimeUnit unit) {
        executeWithMonitor("setWithExpire", key, () -> {
            stringRedisTemplate.opsForValue().set(buildKey(key), value, timeout, unit);
            return null;
        });
    }

    /**
     * 获取String值
     */
    public String get(String key) {
        return executeWithMonitor("get", key, () -> stringRedisTemplate.opsForValue().get(buildKey(key)));
    }

    /**
     * 设置对象值
     */
    public <T> void setObject(String key, T obj) {
        executeWithMonitor("setObject", key, () -> {
            redisTemplate.opsForValue().set(buildKey(key), obj);
            return null;
        });
    }

    /**
     * 设置对象值并指定过期时间
     */
    public <T> void setObject(String key, T obj, long timeout, TimeUnit unit) {
        executeWithMonitor("setObjectWithExpire", key, () -> {
            redisTemplate.opsForValue().set(buildKey(key), obj, timeout, unit);
            return null;
        });
    }

    /**
     * 获取对象值
     */
    @SuppressWarnings("unchecked")
    public <T> T getObject(String key, Class<T> clazz) {
        return executeWithMonitor("getObject", key, () -> {
            Object obj = redisTemplate.opsForValue().get(buildKey(key));
            return obj != null ? (T) obj : null;
        });
    }

    /**
     * 自增操作
     */
    public Long increment(String key) {
        return executeWithMonitor("increment", key, () -> stringRedisTemplate.opsForValue().increment(buildKey(key)));
    }

    /**
     * 自增指定步长
     */
    public Long increment(String key, long delta) {
        return executeWithMonitor("incrementBy", key,
                () -> stringRedisTemplate.opsForValue().increment(buildKey(key), delta));
    }

    // ==================== 分布式锁相关操作 ====================

    /**
     * 尝试获取分布式锁
     */
    public Boolean tryLock(String lockKey, String requestId, long expireTime, TimeUnit unit) {
        return executeWithMonitor("tryLock", lockKey, () -> {
            String fullKey = buildKey("lock:" + lockKey);
            Boolean result = stringRedisTemplate.opsForValue().setIfAbsent(fullKey, requestId, expireTime, unit);
            if (Boolean.TRUE.equals(result)) {
                log.debug("成功获取分布式锁: {} requestId: {}", lockKey, requestId);
            }
            return result;
        });
    }

    /**
     * 释放分布式锁
     */
    public Boolean releaseLock(String lockKey, String requestId) {
        return executeWithMonitor("releaseLock", lockKey, () -> {
            String fullKey = buildKey("lock:" + lockKey);
            String script = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end";
            Long result = stringRedisTemplate.execute(
                    new DefaultRedisScript<>(script, Long.class),
                    Collections.singletonList(fullKey),
                    requestId);
            boolean released = result != null && result == 1L;
            if (released) {
                log.debug("成功释放分布式锁: {} requestId: {}", lockKey, requestId);
            }
            return released;
        });
    }

    // ==================== 中文Key双向转换 ====================

    /**
     * 解码Redis中的编码key，还原为原始key
     *
     * @param encodedKey Redis中存储的编码后的key（包含应用前缀）
     * @return 原始的key，如果无法解码则返回去除前缀后的key
     */
    public String decodeKey(String encodedKey) {
        if (StringUtils.isBlank(encodedKey)) {
            return encodedKey;
        }

        // 移除应用前缀
        String keyWithoutPrefix = encodedKey;
        if (encodedKey.startsWith(keyPrefix)) {
            keyWithoutPrefix = encodedKey.substring(keyPrefix.length());
        }

        // 检查是否为Base64编码格式
        if (keyWithoutPrefix.startsWith("b64_")) {
            return decodeBase64Key(keyWithoutPrefix);
        }

        // 非编码格式，直接返回
        return keyWithoutPrefix;
    }

    /**
     * 解码Base64格式的key
     */
    private String decodeBase64Key(String encodedKey) {
        try {
            // 去掉 "b64_" 前缀
            String base64Part = encodedKey.substring(4);
            byte[] decodedBytes = Base64.getDecoder().decode(base64Part);
            return new String(decodedBytes, StandardCharsets.UTF_8);
        } catch (Exception e) {
            log.warn("Base64解码失败: {}, 错误: {}", encodedKey, e.getMessage());
            return encodedKey;
        }
    }

    /**
     * 批量解码Redis key
     */
    public Map<String, String> decodeKeys(Collection<String> encodedKeys) {
        if (encodedKeys == null || encodedKeys.isEmpty()) {
            return Collections.emptyMap();
        }

        Map<String, String> result = new LinkedHashMap<>();
        for (String encodedKey : encodedKeys) {
            if (StringUtils.isNotBlank(encodedKey)) {
                result.put(encodedKey, decodeKey(encodedKey));
            }
        }
        return result;
    }

    /**
     * 预览key的编码结果（不实际存储）
     */
    public String previewKey(String originalKey) {
        if (StringUtils.isBlank(originalKey)) {
            return originalKey;
        }
        String processedKey = processKey(originalKey);
        String fullKey = keyPrefix + processedKey;

        if (logEnabled) {
            log.debug("key编码预览: 原始='{}' 处理后='{}' 完整key='{}'",
                    originalKey, processedKey, fullKey);
        }
        return fullKey;
    }

    /**
     * 检查key是否为编码格式
     */
    public boolean isEncodedKey(String key) {
        return StringUtils.isNotBlank(key) && key.contains("b64_");
    }

    /**
     * 检查给定的key是否包含中文
     */
    public boolean isChineseKey(String key) {
        return containsChinese(key);
    }

    // ==================== 工具方法 ====================

    /**
     * 获取当前配置的key前缀
     */
    public String getKeyPrefix() {
        return keyPrefix;
    }

    /**
     * 生成唯一标识符（用于分布式锁等场景）
     */
    public String generateUniqueId() {
        return UUID.randomUUID().toString().replace("-", "");
    }
}