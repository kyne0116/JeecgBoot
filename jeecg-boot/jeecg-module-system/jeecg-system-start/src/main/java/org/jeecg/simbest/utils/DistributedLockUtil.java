package org.jeecg.simbest.utils;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.simbest.config.AppConfig;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Component;

import java.net.InetAddress;
import java.time.Duration;
import java.util.Collections;
import java.util.UUID;

/**
 * Redis分布式锁工具类
 * 用于解决集群环境下定时任务重复执行的问题
 *
 * @author JeecgBoot
 * @since 2025-08-19
 */
@Slf4j
@Component
public class DistributedLockUtil {

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @Autowired
    private AppConfig appConfig;

    /**
     * 分布式锁前缀（动态生成，包含应用名称）
     */
    private String lockPrefix;

    /**
     * 默认锁过期时间（分钟）
     */
    private static final long DEFAULT_EXPIRE_MINUTES = 30;

    @PostConstruct
    public void init() {
        // 动态构建分布式锁前缀，格式：{应用名}:distributed:lock:
        this.lockPrefix = appConfig.getAppcode() + ":distributed:lock:";
        log.info("DistributedLockUtil初始化完成，分布式锁前缀: {}", this.lockPrefix);
    }

    /**
     * Lua脚本：释放锁（确保原子性）
     */
    private static final String UNLOCK_SCRIPT =
        "if redis.call('get', KEYS[1]) == ARGV[1] then " +
        "    return redis.call('del', KEYS[1]) " +
        "else " +
        "    return 0 " +
        "end";

    /**
     * 获取分布式锁
     *
     * @param lockKey 锁的键名
     * @param expireMinutes 锁的过期时间（分钟）
     * @return 锁的值（成功时返回UUID，失败时返回null）
     */
    public String acquireLock(String lockKey, long expireMinutes) {
        try {
            String fullLockKey = lockPrefix + lockKey;
            String lockValue = generateLockValue();

            // 尝试获取锁
            Boolean acquired = redisTemplate.opsForValue()
                .setIfAbsent(fullLockKey, lockValue, Duration.ofMinutes(expireMinutes));

            if (Boolean.TRUE.equals(acquired)) {
                log.info("[DistributedLock] 成功获取分布式锁 - Key: {}, Value: {}, 过期时间: {}分钟",
                    fullLockKey, lockValue, expireMinutes);
                return lockValue;
            } else {
                log.info("[DistributedLock] 获取分布式锁失败，其他节点正在执行 - Key: {}", fullLockKey);
                return null;
            }
        } catch (Exception e) {
            log.error("[DistributedLock] 获取分布式锁异常 - Key: {}", lockKey, e);
            return null;
        }
    }

    /**
     * 获取分布式锁（使用默认过期时间）
     *
     * @param lockKey 锁的键名
     * @return 锁的值（成功时返回UUID，失败时返回null）
     */
    public String acquireLock(String lockKey) {
        return acquireLock(lockKey, DEFAULT_EXPIRE_MINUTES);
    }

    /**
     * 释放分布式锁
     *
     * @param lockKey 锁的键名
     * @param lockValue 锁的值
     * @return 是否释放成功
     */
    public boolean releaseLock(String lockKey, String lockValue) {
        try {
            if (lockValue == null) {
                log.warn("[DistributedLock] 锁值为空，无需释放 - Key: {}", lockKey);
                return false;
            }

            String fullLockKey = lockPrefix + lockKey;

            // 使用Lua脚本确保原子性
            DefaultRedisScript<Long> script = new DefaultRedisScript<>();
            script.setScriptText(UNLOCK_SCRIPT);
            script.setResultType(Long.class);

            Long result = redisTemplate.execute(script,
                Collections.singletonList(fullLockKey), lockValue);

            boolean released = result != null && result > 0;
            if (released) {
                log.info("[DistributedLock] 成功释放分布式锁 - Key: {}, Value: {}",
                    fullLockKey, lockValue);
            } else {
                log.warn("[DistributedLock] 释放分布式锁失败，锁可能已过期或被其他节点持有 - Key: {}, Value: {}",
                    fullLockKey, lockValue);
            }

            return released;
        } catch (Exception e) {
            log.error("[DistributedLock] 释放分布式锁异常 - Key: {}, Value: {}", lockKey, lockValue, e);
            return false;
        }
    }

    /**
     * 生成锁的值（包含节点信息）
     *
     * @return 锁的唯一值
     */
    private String generateLockValue() {
        try {
            String hostInfo = InetAddress.getLocalHost().getHostAddress();
            String uuid = UUID.randomUUID().toString();
            return hostInfo + ":" + uuid;
        } catch (Exception e) {
            log.warn("[DistributedLock] 获取主机信息失败，使用UUID作为锁值", e);
            return UUID.randomUUID().toString();
        }
    }

    /**
     * 检查锁是否存在
     *
     * @param lockKey 锁的键名
     * @return 锁是否存在
     */
    public boolean isLockExists(String lockKey) {
        try {
            String fullLockKey = lockPrefix + lockKey;
            return Boolean.TRUE.equals(redisTemplate.hasKey(fullLockKey));
        } catch (Exception e) {
            log.error("[DistributedLock] 检查锁是否存在异常 - Key: {}", lockKey, e);
            return false;
        }
    }

    /**
     * 获取锁的剩余过期时间
     *
     * @param lockKey 锁的键名
     * @return 剩余过期时间（秒），-1表示永不过期，-2表示不存在
     */
    public long getLockTtl(String lockKey) {
        try {
            String fullLockKey = lockPrefix + lockKey;
            return redisTemplate.getExpire(fullLockKey);
        } catch (Exception e) {
            log.error("[DistributedLock] 获取锁过期时间异常 - Key: {}", lockKey, e);
            return -2;
        }
    }

    /**
     * 强制释放锁（谨慎使用）
     *
     * @param lockKey 锁的键名
     * @return 是否删除成功
     */
    public boolean forceReleaseLock(String lockKey) {
        try {
            String fullLockKey = lockPrefix + lockKey;
            Boolean deleted = redisTemplate.delete(fullLockKey);

            if (Boolean.TRUE.equals(deleted)) {
                log.warn("[DistributedLock] 强制释放分布式锁成功 - Key: {}", fullLockKey);
            } else {
                log.warn("[DistributedLock] 强制释放分布式锁失败，锁可能不存在 - Key: {}", fullLockKey);
            }

            return Boolean.TRUE.equals(deleted);
        } catch (Exception e) {
            log.error("[DistributedLock] 强制释放分布式锁异常 - Key: {}", lockKey, e);
            return false;
        }
    }
}
