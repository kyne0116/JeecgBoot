package org.jeecg.modules.system.controller;

import cn.hutool.core.util.StrUtil;
import com.alibaba.fastjson.JSONObject;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.jeecg.common.api.vo.Result;
import org.jeecg.common.constant.CommonConstant;
import org.jeecg.common.exception.JeecgBootException;
import org.jeecg.common.system.util.JwtUtil;
import org.jeecg.common.util.EncryptorUtil;
import org.jeecg.common.util.RedisUtil;
import org.jeecg.modules.base.service.BaseCommonService;
import org.jeecg.modules.system.entity.SysDepart;
import org.jeecg.modules.system.entity.SysUser;
import org.jeecg.modules.system.service.ISysDepartService;
import org.jeecg.modules.system.service.ISysUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.net.URLEncoder;
import java.util.LinkedHashMap;
import java.util.List;

/**
 * SSO单点登录控制器
 *
 * @author SIMBEST
 * @date 2025-09-08
 */
@RestController
@RequestMapping("/sys/sso")
@Tag(name = "SSO单点登录")
@Slf4j
public class SsoLoginController {

    @Autowired
    private ISysUserService sysUserService;

    @Autowired
    private ISysDepartService sysDepartService;

    @Autowired
    private RedisUtil redisUtil;

    @Autowired
    private BaseCommonService baseCommonService;

    /*
     * 页面单点：webauth模式（后端主导）
     * http://localhost:8080/jeecg-boot/sys/sso/webauth?sso_data=79C023386BAC6785E7EBD524110262678F770CF81CAB43EA38579DDF839A57B84C0EA0A80871598A5848A78546CBFD3D5A97AA48EBF7C845FC59BBFB8698327F&redirectUrl=http://localhost:3100/dashboard
     *
     * 页面单点：apiauth模式（前端主导）
     * http://localhost:3100/dashboard/analysis?sso=true&sso_mode=apiauth&sso_data=79138138A9ACAF75C7AC9924FD0AB0A036770C6A1CAB151408571641679AFE20A98D70C8684211BD5848A96038CB0778CD97AA48EBF7C8879B5FBBFB7798FCFD
     *
     * http://localhost:3100/data-analysis/chart-design-workflow?sso=true&sso_mode=apiauth&sso_data=79138138A9ACAF75C7AC9924FD0AB0A036770C6A1CAB151408571641679AFE20A98D70C8684211BD5848A96038CB0778CD97AA48EBF7C8879B5FBBFB7798FCFD
     *
     *
     * 接口单点：
     * 第一步：获取token 请求 http://localhost:8080/jeecg-boot/sys/sso/apiauth?sso_data= + 加密用户账号encryptedUsername
     * 第二步：携带token 访问所需接口，例如：http://localhost:8080/jeecg-boot/datas/indicatorDashboard/list 注意携带认证头，参数：X-Access-Token 值：上一步获取的token
     * 登录成功：返回数据
     *
     */
    public static void main(String[] args) {
        System.out.println("=== SSO加密数据生成 ===\n");
        String[] users = {"admin", "jeecg", "test"};
        for (String user : users) {
            String encrypted = EncryptorUtil.encode("SIMBEST_SSO", user);
            System.out.println("用户: " + user + " => " + encrypted);
        }
    }

    /**
     * SSO单点登录接口 - webauth模式（后端主导）
     *
     * 【主导方】：后端主导，通过URL重定向完成单点登录
     * 【使用方式】：第三方系统直接访问此接口，后端验证后重定向到前端页面并携带token
     * 【前端代码影响】：前端无需改造，路由守卫自动处理
     * 【适用场景】：
     *   - 传统网站页面跳转集成
     *   - 门户系统中的链接跳转
     *   - 第三方系统快速集成（无需前端开发）
     *   - 支持跳转到任意前端页面
     *
     * 示例用法：
     * GET /sys/sso/webauth?sso_data={加密用户名}&redirectUrl=http://localhost:3100/dashboard
     * GET /sys/sso/webauth?sso_data={加密用户名}&redirectUrl=http://localhost:3100/data-analysis/chart-design-workflow
     *
     * 处理流程：
     * 1. 后端解密用户名，验证用户身份
     * 2. 生成JWT token并重定向到前端页面
     * 3. 前端路由守卫自动检测URL中的SSO参数并完成登录
     *
     * 成功重定向：{redirectUrl}?sso=true&sso_mode=webauth&sso_data={jwtToken}
     * 失败重定向：{redirectUrl}?sso=true&sso_mode=webauth&sso_error={errorMessage}
     */
    @Operation(summary = "SSO单点登录 - webauth模式（后端主导）")
    @GetMapping("/webauth")
    public void webauth(@RequestParam("sso_data") String ssoData,
                        @RequestParam("redirectUrl") String redirectUrl,
                        HttpServletRequest request,
                        HttpServletResponse response) throws IOException {

        log.info("【SSO webauth】请求 - IP:{}, 重定向:{}", getClientIpAddress(request), redirectUrl);

        String decryptedUsername = null;
        try {
            decryptedUsername = EncryptorUtil.decode("SIMBEST_SSO", ssoData, 1800);
            log.info("【SSO webauth】解密成功 - 用户名: {}", decryptedUsername);
        } catch (Exception e) {
            log.error("【SSO webauth】解密失败 - {}: {}", e.getClass().getSimpleName(), e.getMessage());
            String errorUrl = buildUnifiedErrorUrl(redirectUrl, "webauth", "单点登录令牌无效或已过期");
            response.sendRedirect(errorUrl);
            return;
        }

        try {
            Result<JSONObject> result = performSsoLogin(decryptedUsername, request);

            if (result.isSuccess()) {
                JSONObject loginResult = result.getResult();
                String token = loginResult.getString("token");

                if (StringUtils.isBlank(redirectUrl)) {
                    throw new JeecgBootException("重定向地址不能为空");
                }

                String targetUrl = buildUnifiedRedirectUrl(redirectUrl, "webauth", token, null);
                log.info("【SSO webauth】登录成功 - 用户名:{}, 重定向:{}", decryptedUsername, targetUrl);
                response.sendRedirect(targetUrl);
            } else {
                if (StringUtils.isBlank(redirectUrl)) {
                    response.getWriter().write("登录失败且重定向地址为空");
                    return;
                }

                String errorUrl = buildUnifiedErrorUrl(redirectUrl, "webauth", result.getMessage());
                log.warn("【SSO webauth】登录失败 - 用户名:{}, 原因:{}", decryptedUsername, result.getMessage());
                response.sendRedirect(errorUrl);
            }
        } catch (Exception e) {
            log.error("【SSO webauth】登录异常 - 用户名:{}, {}: {}", decryptedUsername, e.getClass().getSimpleName(), e.getMessage());
            if (StringUtils.isBlank(redirectUrl)) {
                response.getWriter().write("系统异常且重定向地址为空");
                return;
            }

            String errorUrl = buildUnifiedErrorUrl(redirectUrl, "webauth", "系统异常，请稍后重试");
            response.sendRedirect(errorUrl);
        }
    }

    /**
     * SSO单点登录API接口 - apiauth模式（前端主导）
     *
     * 【主导方】：前端主导，通过AJAX调用获取用户身份token
     * 【使用方式】：用户直接访问前端页面，路由守卫自动检测SSO参数并处理登录
     * 【前端代码影响】：路由守卫全局自动处理，无需手动集成
     * 【适用场景】：
     *   - 单页应用（SPA）集成
     *   - 前后端分离架构的灵活集成
     *   - 需要精确控制登录时机和行为
     *   - 支持从任意页面直接访问
     *
     * 前端集成方式：
     * 用户直接访问前端页面，路由守卫自动检测SSO参数并处理登录
     *
     * 示例用法：
     * GET  /sys/sso/apiauth?sso_data={加密用户名}
     * POST /sys/sso/apiauth
     *      Content-Type: application/x-www-form-urlencoded
     *      sso_data={加密用户名}
     *
     * 处理流程：
     * 1. 前端路由守卫检测URL中的sso_data参数
     * 2. 调用此API接口验证用户身份
     * 3. 返回完整的用户信息和token
     * 4. 前端设置token和用户信息到store
     *
     * 响应格式：
     * 成功：{"success":true, "result":{"token":"...", "userInfo":{...}, "departs":[...]}}
     * 失败：{"success":false, "message":"错误信息"}
     */
    @Operation(summary = "SSO单点登录 - apiauth模式（前端主导）")
    @RequestMapping(value = "/apiauth", method = {RequestMethod.GET, RequestMethod.POST})
    public Result<JSONObject> apiauth(@RequestParam("sso_data") String ssoData,
                                      HttpServletRequest request) {

        log.info("【SSO apiauth】请求 - IP:{}, 方法:{}, URI:{}, 数据长度:{}",
                getClientIpAddress(request), request.getMethod(), request.getRequestURI(),
                ssoData != null ? ssoData.length() : 0);

        String decryptedUsername = null;
        try {
            decryptedUsername = EncryptorUtil.decode("SIMBEST_SSO", ssoData, 1800);
            log.info("【SSO apiauth】解密成功 - 用户名: {}", decryptedUsername);
        } catch (Exception e) {
            log.error("【SSO apiauth】解密失败 - {}: {}", e.getClass().getSimpleName(), e.getMessage());
            return Result.error("单点登录令牌无效或已过期");
        }

        try {
            Result<JSONObject> result = performSsoLogin(decryptedUsername, request);
            if (result.isSuccess()) {
                log.info("【SSO apiauth】登录成功 - 用户名: {}", decryptedUsername);
            } else {
                log.warn("【SSO apiauth】登录失败 - 用户名: {}, 原因: {}", decryptedUsername, result.getMessage());
            }
            return result;
        } catch (Exception e) {
            log.error("【SSO apiauth】登录异常 - 用户名: {}, {}: {}", decryptedUsername, e.getClass().getSimpleName(), e.getMessage());
            return Result.error("系统异常，请稍后重试");
        }
    }

    /**
     * 执行SSO登录核心逻辑
     */
    private Result<JSONObject> performSsoLogin(String username, HttpServletRequest request) {
        Result<JSONObject> result = new Result<>();

        if (StrUtil.isBlank(username)) {
            log.error("【SSO登录】用户名为空");
            return result.error500("用户名不能为空");
        }

        LambdaQueryWrapper<SysUser> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(SysUser::getUsername, username);
        SysUser sysUser = sysUserService.getOne(queryWrapper);

        if (sysUser == null) {
            log.error("【SSO登录】用户不存在 - 用户名: {}", username);
            return result.error500("用户不存在");
        }
        log.info("【SSO登录】查询用户 - ID:{}, 用户名:{}, 姓名:{}, 状态:{}", sysUser.getId(), sysUser.getUsername(), sysUser.getRealname(), sysUser.getStatus());

        result = sysUserService.checkUserIsEffective(sysUser);
        if (!result.isSuccess()) {
            log.error("【SSO登录】用户校验失败 - 用户名:{}, 原因:{}", username, result.getMessage());
            return result;
        }

        try {
            String token = JwtUtil.sign(username, sysUser.getPassword());
            String tokenKey = CommonConstant.PREFIX_USER_TOKEN + token;
            redisUtil.set(tokenKey, token);
            long expireTime = JwtUtil.EXPIRE_TIME * 2 / 1000;
            redisUtil.expire(tokenKey, expireTime);
            log.info("【SSO登录】Token生成 - 用户名:{}, 过期时间:{}秒", username, expireTime);

            JSONObject obj = new JSONObject(new LinkedHashMap<>());
            obj.put("token", token);
            obj.put("userInfo", sysUser);

            List<SysDepart> departs = sysDepartService.queryUserDeparts(sysUser.getId());
            obj.put("departs", departs);
            if (departs == null || departs.size() == 0) {
                obj.put("multi_depart", 0);
            } else if (departs.size() == 1) {
                sysUserService.updateUserDepart(username, departs.get(0).getOrgCode(), null);
                obj.put("multi_depart", 1);
            } else {
                obj.put("multi_depart", 2);
            }
            log.info("【SSO登录】部门信息 - 用户名:{}, 部门数:{}", username, departs != null ? departs.size() : 0);

            result.setResult(obj);
            result.success("SSO登录成功");

            String logMsg = String.format("用户名: %s, SSO单点登录成功！", username);
            baseCommonService.addLog(logMsg, CommonConstant.LOG_TYPE_1, null);

            return result;
        } catch (Exception e) {
            log.error("【SSO登录】Token生成异常 - 用户名:{}, {}: {}", username, e.getClass().getSimpleName(), e.getMessage());
            return result.error500("Token生成失败: " + e.getMessage());
        }
    }

    /**
     * 构建统一格式的重定向URL
     * @param redirectUrl 目标URL
     * @param mode SSO模式
     * @param data SSO数据（token等）
     * @param targetPath 目标路径（可选）
     * @return 统一格式的URL
     */
    private String buildUnifiedRedirectUrl(String redirectUrl, String mode, String data, String targetPath) {
        try {
            String separator = redirectUrl.contains("?") ? "&" : "?";
            StringBuilder url = new StringBuilder(redirectUrl);
            url.append(separator);
            url.append("sso=true");
            url.append("&sso_mode=").append(mode);
            url.append("&sso_data=").append(URLEncoder.encode(data, "UTF-8"));
            if (StringUtils.isNotBlank(targetPath)) {
                url.append("&sso_redirect=").append(URLEncoder.encode(targetPath, "UTF-8"));
            }
            return url.toString();
        } catch (Exception e) {
            log.error("构建统一重定向URL失败", e);
            throw new JeecgBootException("构建重定向URL失败");
        }
    }

    /**
     * 构建统一格式的错误URL
     * @param redirectUrl 目标URL
     * @param mode SSO模式
     * @param errorMessage 错误信息
     * @return 统一格式的错误URL
     */
    private String buildUnifiedErrorUrl(String redirectUrl, String mode, String errorMessage) {
        try {
            String separator = redirectUrl.contains("?") ? "&" : "?";
            StringBuilder url = new StringBuilder(redirectUrl);
            url.append(separator);
            url.append("sso=true");
            url.append("&sso_mode=").append(mode);
            url.append("&sso_error=").append(URLEncoder.encode(errorMessage, "UTF-8"));
            return url.toString();
        } catch (Exception e) {
            log.error("构建统一错误URL失败", e);
            throw new JeecgBootException("构建错误URL失败");
        }
    }

    /**
     * 获取客户端真实IP地址
     */
    private String getClientIpAddress(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        String xRealIP = request.getHeader("X-Real-IP");
        String remoteAddr = request.getRemoteAddr();

        if (StrUtil.isNotBlank(xForwardedFor) && !"unknown".equalsIgnoreCase(xForwardedFor)) {
            return xForwardedFor.split(",")[0].trim();
        } else if (StrUtil.isNotBlank(xRealIP) && !"unknown".equalsIgnoreCase(xRealIP)) {
            return xRealIP;
        } else {
            return remoteAddr;
        }
    }


}
