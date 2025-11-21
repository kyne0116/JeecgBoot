package org.jeecg.simbest.token;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import jakarta.annotation.PostConstruct;

import org.apache.commons.lang.StringUtils;
import org.jeecg.common.util.RedisUtil;
import org.jeecg.common.util.RestUtil;
import org.jeecg.simbest.config.AppConfig;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;

import com.alibaba.fastjson.JSONObject;

import lombok.extern.slf4j.Slf4j;

/**
 * Simbest应用Token管理类
 * 提供获取和缓存第三方应用access token的功能
 *
 * @author jeecg-boot
 */
@Slf4j
@Component
public class SimbestAppToken {

    @Autowired
    private RedisUtil redisUtil;

    @Autowired
    private AppConfig appConfig;

    private static SimbestAppToken instance;

    // 用于防止并发请求同一appcode时的重复调用
    private static final ConcurrentHashMap<String, ReentrantLock> lockMap = new ConcurrentHashMap<>();

    // Redis缓存key前缀（动态生成，包含应用名称）
    private String cacheKeyPrefix;

    // 默认缓存过期时间偏移量（秒），比expires_in少60秒以避免边界问题
    private static final int CACHE_EXPIRE_OFFSET = 60;

    @PostConstruct
    public void init() {
        instance = this;
        // 动态构建Redis缓存key前缀，格式：{应用名}:simbest:token:
        this.cacheKeyPrefix = appConfig.getAppcode() + ":simbest:token:";
        log.info("SimbestAppToken初始化完成，Redis缓存key前缀: {}", this.cacheKeyPrefix);
    }

    /**
     * TokenResponse内部类，用于封装access token响应信息
     */
    public static class TokenResponse {
        private String accessToken;
        private String tokenType;
        private Integer expiresIn;
        private String scope;

        public TokenResponse() {
        }

        public TokenResponse(String accessToken, String tokenType, Integer expiresIn, String scope) {
            this.accessToken = accessToken;
            this.tokenType = tokenType;
            this.expiresIn = expiresIn;
            this.scope = scope;
        }

        // Getters and Setters
        public String getAccessToken() {
            return accessToken;
        }

        public void setAccessToken(String accessToken) {
            this.accessToken = accessToken;
        }

        public String getTokenType() {
            return tokenType;
        }

        public void setTokenType(String tokenType) {
            this.tokenType = tokenType;
        }

        public Integer getExpiresIn() {
            return expiresIn;
        }

        public void setExpiresIn(Integer expiresIn) {
            this.expiresIn = expiresIn;
        }

        public String getScope() {
            return scope;
        }

        public void setScope(String scope) {
            this.scope = scope;
        }

        @Override
        public String toString() {
            return "TokenResponse{" +
                    "accessToken='" + accessToken + '\'' +
                    ", tokenType='" + tokenType + '\'' +
                    ", expiresIn=" + expiresIn +
                    ", scope='" + scope + '\'' +
                    '}';
        }
    }

    /**
     * 获取access token
     *
     * @param appcode 应用代码，作为Redis缓存key
     * @param appurl  获取token的API端点URL
     * @return 包含access token信息的TokenResponse对象
     * @throws IllegalArgumentException 当参数无效时抛出
     * @throws RuntimeException         当网络请求失败或响应解析错误时抛出
     */
    public static TokenResponse getAccessToken(String appcode, String appurl) {
        // 1. 参数验证
        if (StringUtils.isBlank(appcode)) {
            throw new IllegalArgumentException("appcode不能为空或null");
        }
        if (StringUtils.isBlank(appurl)) {
            throw new IllegalArgumentException("appurl不能为空或null");
        }

        log.info("开始获取access token，appcode: {}, appurl: {}", appcode, appurl);

        // 获取锁，防止并发请求同一appcode时的重复调用
        ReentrantLock lock = lockMap.computeIfAbsent(appcode, k -> new ReentrantLock());
        lock.lock();

        try {
            // 2. Redis缓存查询
            String cacheKey = instance.cacheKeyPrefix + appcode;
            if (instance.redisUtil.hasKey(cacheKey)) {
                log.info("从Redis缓存中获取token，key: {}", cacheKey);
                Object cachedToken = instance.redisUtil.get(cacheKey);
                if (cachedToken instanceof JSONObject) {
                    JSONObject tokenJson = (JSONObject) cachedToken;
                    TokenResponse tokenResponse = parseTokenResponse(tokenJson);
                    log.info("缓存命中，返回已缓存的token: {}", tokenResponse);
                    return tokenResponse;
                }
            }

            // 3. 缓存未命中，向API发送POST请求获取新token
            log.info("缓存未命中，向API请求新的access token");
            TokenResponse newToken = requestNewToken(appurl);

            // 4. 将新token存储到Redis中
            cacheTokenToRedis(cacheKey, newToken);

            log.info("成功获取并缓存新的access token: {}", newToken);
            return newToken;

        } catch (Exception e) {
            log.error("获取access token失败，appcode: {}, appurl: {}", appcode, appurl, e);
            throw new RuntimeException("获取access token失败: " + e.getMessage(), e);
        } finally {
            lock.unlock();
            // 清理锁映射，避免内存泄漏
            if (!lock.hasQueuedThreads()) {
                lockMap.remove(appcode);
            }
        }
    }

    /**
     * 向API发送POST请求获取新的access token
     *
     * @param appurl API端点URL
     * @return TokenResponse对象
     * @throws RuntimeException 当请求失败或响应解析错误时抛出
     */
    private static TokenResponse requestNewToken(String appurl) {
        try {
            log.info("向API发送POST请求获取token，URL: {}", appurl);

            // 使用JeecgBoot框架的RestUtil发送POST请求
            ResponseEntity<JSONObject> response = RestUtil.postNative(appurl, null, null);

            if (response == null || response.getBody() == null) {
                throw new RuntimeException("API响应为空");
            }

            JSONObject responseBody = response.getBody();
            log.info("API响应: {}", responseBody);

            // 验证响应是否包含必要字段
            if (!responseBody.containsKey("access_token")) {
                throw new RuntimeException("API响应中缺少access_token字段: " + responseBody);
            }

            return parseTokenResponse(responseBody);

        } catch (Exception e) {
            log.error("请求新token失败，URL: {}", appurl, e);
            throw new RuntimeException("请求新token失败: " + e.getMessage(), e);
        }
    }

    /**
     * 解析JSON响应为TokenResponse对象
     *
     * @param jsonResponse JSON响应对象
     * @return TokenResponse对象
     */
    private static TokenResponse parseTokenResponse(JSONObject jsonResponse) {
        try {
            String accessToken = jsonResponse.getString("access_token");
            String tokenType = jsonResponse.getString("token_type");
            Integer expiresIn = jsonResponse.getInteger("expires_in");
            String scope = jsonResponse.getString("scope");

            if (StringUtils.isBlank(accessToken)) {
                throw new RuntimeException("access_token字段为空");
            }

            return new TokenResponse(accessToken, tokenType, expiresIn, scope);

        } catch (Exception e) {
            log.error("解析token响应失败: {}", jsonResponse, e);
            throw new RuntimeException("解析token响应失败: " + e.getMessage(), e);
        }
    }

    /**
     * 将token信息缓存到Redis中
     *
     * @param cacheKey      Redis缓存key
     * @param tokenResponse token响应对象
     */
    private static void cacheTokenToRedis(String cacheKey, TokenResponse tokenResponse) {
        try {
            // 构建缓存的JSON对象
            JSONObject cacheData = new JSONObject();
            cacheData.put("access_token", tokenResponse.getAccessToken());
            cacheData.put("token_type", tokenResponse.getTokenType());
            cacheData.put("expires_in", tokenResponse.getExpiresIn());
            cacheData.put("scope", tokenResponse.getScope());

            // 计算缓存过期时间（比expires_in少60秒以避免边界问题）
            int cacheExpireSeconds = tokenResponse.getExpiresIn() != null
                    ? Math.max(tokenResponse.getExpiresIn() - CACHE_EXPIRE_OFFSET, 60)
                    : 3600;

            // 存储到Redis
            instance.redisUtil.set(cacheKey, cacheData);
            instance.redisUtil.expire(cacheKey, cacheExpireSeconds);

            log.info("Token已缓存到Redis，key: {}, 过期时间: {}秒", cacheKey, cacheExpireSeconds);

        } catch (Exception e) {
            log.error("缓存token到Redis失败，key: {}", cacheKey, e);
            // 缓存失败不影响主流程，只记录错误日志
        }
    }
}
