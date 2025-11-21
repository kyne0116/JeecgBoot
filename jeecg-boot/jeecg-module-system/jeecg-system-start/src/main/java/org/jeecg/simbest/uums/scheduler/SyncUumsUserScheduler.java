package org.jeecg.simbest.uums.scheduler;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

import jakarta.servlet.http.HttpServletRequest;
import org.jeecg.common.constant.CommonConstant;
import org.jeecg.common.util.PasswordUtil;
import org.jeecg.common.util.DateUtils;
import org.jeecg.common.util.IpUtils;
import org.jeecg.common.util.RestUtil;
import org.jeecg.common.util.SpringContextUtils;
import org.jeecg.common.util.oConvertUtils;
import org.jeecg.modules.base.service.BaseCommonService;
import org.jeecg.simbest.config.AppConfig;
import org.jeecg.simbest.token.SimbestAppToken;
import org.jeecg.simbest.uums.entity.UumsChangeUserLog;
import org.jeecg.simbest.uums.service.IUumsChangeUserLogService;
import org.jeecg.simbest.utils.DistributedLockUtil;
import org.jeecg.modules.system.entity.SysDepart;
import org.jeecg.modules.system.entity.SysRole;
import org.jeecg.modules.system.entity.SysUser;
import org.jeecg.modules.system.entity.SysUserDepart;
import org.jeecg.modules.system.entity.SysUserRole;
import org.jeecg.modules.system.service.ISysDepartService;
import org.jeecg.modules.system.service.ISysRoleService;
import org.jeecg.modules.system.service.ISysUserDepartService;
import org.jeecg.modules.system.service.ISysUserRoleService;
import org.jeecg.modules.system.service.ISysUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import com.alibaba.fastjson.JSONObject;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;

import lombok.extern.slf4j.Slf4j;

import static org.jeecg.simbest.constants.SimbestConstants.*;

@Slf4j
@Component
public class SyncUumsUserScheduler {

    @Autowired
    private AppConfig appConfig;

    @Autowired
    private IUumsChangeUserLogService uumsChangeUserLogService;

    @Autowired
    private ISysUserService sysUserService;

    @Autowired
    private ISysDepartService sysDepartService;

    @Autowired
    private ISysUserDepartService sysUserDepartService;

    @Autowired
    private ISysRoleService sysRoleService;

    @Autowired
    private ISysUserRoleService sysUserRoleService;

    @Autowired
    private DistributedLockUtil distributedLockUtil;

    @Autowired
    private BaseCommonService baseCommonService;

    /**
     * 定时同步UUMS用户数据
     * Cron表达式通过配置文件 jeecg.uums.scheduler.user-sync-cron 配置
     * 默认每天凌晨2点执行：0 0 2 * * ?
     */
    @Scheduled(cron = "${jeecg.uums.scheduler.user-sync-cron:0 0 2 * * ?}")
    public void syncUumsUsers() {
        String lockKey = "sync_uums_users";
        String lockValue = null;
        
        try {
            // 尝试获取分布式锁
            lockValue = distributedLockUtil.acquireLock(lockKey, 30);
            
            if (lockValue != null) {
                String uumsAddress = appConfig.getUumsAddress();
                log.info("[SyncUumsUserScheduler] 获取分布式锁成功，定时任务开始执行 - UUMS系统地址: {}", uumsAddress);
                
                // 执行同步任务：同步上一日到今日的数据
                Date currentDate = new Date();
                Calendar calendar = Calendar.getInstance();
                calendar.setTime(currentDate);
                
                // 获取今日
                String endDate = DateUtils.formatDate(currentDate, "yyyy-MM-dd");
                
                // 获取上一日
                calendar.add(Calendar.DAY_OF_MONTH, -1);
                Date yesterdayDate = calendar.getTime();
                String startDate = DateUtils.formatDate(yesterdayDate, "yyyy-MM-dd");
                
                log.info("[SyncUumsUserScheduler] 同步时间范围: {} ~ {}", startDate, endDate);
                syncUumsUsers(startDate, endDate);
                
                log.info("[SyncUumsUserScheduler] 定时任务执行完成");
            } else {
                log.info("[SyncUumsUserScheduler] 未获取到分布式锁，其他节点正在执行同步任务，跳过本次执行");
                return;
            }
        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 定时任务执行异常", e);
        } finally {
            // 释放分布式锁
            if (lockValue != null) {
                distributedLockUtil.releaseLock(lockKey, lockValue);
            }
        }
    }

    /**
     * 同步UUMS用户变更数据
     *
     * @param startDate 开始日期
     * @param endDate   结束日期
     * @return 处理的记录数
     */
    public int syncUumsUsers(String startDate, String endDate) {
        Date taskStartTime = new Date();
        int processedRecords = 0;
        boolean success = false;
        
        try {
            String uumsAddress = appConfig.getUumsAddress();
            log.info("[SyncUumsUserScheduler] 开始同步用户数据 - UUMS系统地址: {}, 时间范围: {} ~ {}",
                    uumsAddress, startDate, endDate);
    
            // 1. 获取访问令牌
            SimbestAppToken.TokenResponse tokenResponse = SimbestAppToken.getAccessToken(
                    APPCODE_UUMS, uumsAddress + OAUTH2_UUMS);
    
            if (tokenResponse == null || tokenResponse.getAccessToken() == null) {
                log.error("[SyncUumsUserScheduler] 获取访问令牌失败");
                return 0;
            }
    
            log.info("[SyncUumsUserScheduler] 成功获取访问令牌");
    
            // 2. 构建请求参数
            JSONObject requestParams = buildRequestParams(startDate, endDate);
            log.info("[SyncUumsUserScheduler] 请求参数: {}", requestParams.toJSONString());
    
            // 3. 发送HTTP请求
            String requestUrl = uumsAddress + UUMS_SYNC_USER;
            ResponseEntity<JSONObject> response = sendHttpRequest(requestUrl, requestParams,
                    tokenResponse.getAccessToken());
    
            if (response == null || response.getBody() == null) {
                log.error("[SyncUumsUserScheduler] HTTP请求失败，响应为空");
                return 0;
            }
    
            JSONObject responseBody = response.getBody();
            log.info("[SyncUumsUserScheduler] 接收到响应: {}", responseBody.toJSONString());
    
            // 4. 处理响应数据
            processedRecords = processResponse(responseBody);
            success = true;
            
            return processedRecords;
    
        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 同步用户数据异常", e);
            return 0;
        } finally {
            // 记录定时任务执行日志
            recordTaskExecutionLog(taskStartTime, processedRecords, success);
        }
    }

    /**
     * 构建请求参数
     */
    private JSONObject buildRequestParams(String startDate, String endDate) {
        JSONObject requestParams = new JSONObject();
        requestParams.put("clientIp", "127.0.0.1");
        requestParams.put("clientCode", "dictd");
        requestParams.put("clientName", "dictd");
        requestParams.put("clientLinkman", "dictd");
        requestParams.put("clientLinkTel", "dictd");
        requestParams.put("clientLinkEmail", "dictd");
        requestParams.put("customLinkman", "dictd");
        requestParams.put("customLinkTel", "dictd");
        requestParams.put("customLinkEmail", "dictd");

        JSONObject data = new JSONObject();
        data.put("startTime", startDate);
        data.put("endTime", endDate);
        requestParams.put("data", data);

        return requestParams;
    }

    /**
     * 发送HTTP请求
     */
    private ResponseEntity<JSONObject> sendHttpRequest(String url, JSONObject params, String accessToken) {
        try {
            // 设置请求头
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.setBearerAuth(accessToken);

            log.info("[SyncUumsUserScheduler] 发送POST请求到: {}", url);

            // 发送POST请求
            return RestUtil.request(url, HttpMethod.POST, headers, null, params, JSONObject.class);

        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 发送HTTP请求异常: {}", e.getMessage(), e);
            return null;
        }
    }

    /**
     * 处理响应数据
     * @return 处理的记录数
     */
    private int processResponse(JSONObject responseBody) {
        try {
            // 检查响应状态
            Integer errcode = responseBody.getInteger("errcode");
            if (errcode == null || errcode != 0) {
                log.error("[SyncUumsUserScheduler] 接口返回错误，errcode: {}, message: {}",
                        errcode, responseBody.getString("message"));
                return 0;
            }

            log.info("[SyncUumsUserScheduler] 接口调用成功: {}", responseBody.getString("message"));

            // 获取数据部分
            JSONObject data = responseBody.getJSONObject("data");
            if (data == null) {
                log.warn("[SyncUumsUserScheduler] 响应中没有data字段");
                return 0;
            }

            Integer totalNum = data.getInteger("totalNum");
            String findDataDate = data.getString("findDataDate");
            log.info("[SyncUumsUserScheduler] 获取到用户变更数据，总数: {}, 查询时间: {}", totalNum, findDataDate);

            // 获取详细数据列表
            com.alibaba.fastjson.JSONArray details = data.getJSONArray("details");
            if (details == null || details.isEmpty()) {
                log.info("[SyncUumsUserScheduler] 没有用户变更数据");
                return 0;
            }

            // 转换并保存数据
            List<UumsChangeUserLog> userLogList = convertToUserLogList(details, findDataDate);
            saveUserLogList(userLogList);

            log.info("[SyncUumsUserScheduler] 成功处理 {} 条用户变更记录", userLogList.size());
            return userLogList.size();

        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 处理响应数据异常", e);
            return 0;
        }
    }

    /**
     * 将JSON数组转换为UumsChangeUserLog对象列表
     */
    private List<UumsChangeUserLog> convertToUserLogList(com.alibaba.fastjson.JSONArray details, String syncDate) {
        List<UumsChangeUserLog> userLogList = new ArrayList<>();
        Date currentDate = new Date();

        for (int i = 0; i < details.size(); i++) {
            try {
                JSONObject detail = details.getJSONObject(i);

                // 将JSON对象转换为UumsChangeUserLog实体
                UumsChangeUserLog userLog = new UumsChangeUserLog();

                // 设置基础字段
                userLog.setCreateTime(currentDate);
                userLog.setUpdateTime(currentDate);
                userLog.setSyncDate(currentDate);

                // 映射UUMS返回的字段到实体字段
                userLog.setChangeType(detail.getString("CHANGETYPE"));
                userLog.setUsername(detail.getString("USERNAME"));
                userLog.setDisplayOrder(detail.getInteger("DISPLAYORDER"));
                userLog.setCurrentOrgCode20(detail.getString("CURRENTORGCODE20"));
                userLog.setEmployeeNumber(detail.getString("EMPLOYEENUMBER"));
                userLog.setPreferredMobile(detail.getString("PREFERREDMOBILE"));
                userLog.setEmail(detail.getString("EMAIL"));
                userLog.setTruename(detail.getString("TRUENAME"));
                userLog.setPreOrgcode(detail.getString("PREORGCODE"));
                userLog.setCurrentOrgcode(detail.getString("CURRENTORGCODE"));
                userLog.setPrePositionName(detail.getString("PREPOSITIONNAME"));
                userLog.setCurrentPositionName(detail.getString("CURRENTPOSITIONNAME"));
                userLog.setPositionName(detail.getString("POSITIONNAME"));

                // 设置备用字段
                userLog.setIreserved1(detail.getString("IRESERVED_1"));
                userLog.setIreserved2(detail.getString("IRESERVED_2"));
                userLog.setIreserved3(detail.getString("IRESERVED_3"));
                userLog.setIreserved4(detail.getString("IRESERVED_4"));
                userLog.setIreserved5(detail.getString("IRESERVED_5"));

                // 设置状态和结果
                userLog.setResult("同步成功");
                userLog.setResultFlag("1"); // 成功标志

                userLogList.add(userLog);

            } catch (Exception e) {
                log.error("[SyncUumsUserScheduler] 转换第{}条记录异常: {}", i, e.getMessage(), e);
            }
        }

        return userLogList;
    }

    /**
     * 批量保存用户变更日志并处理用户操作
     */
    private void saveUserLogList(List<UumsChangeUserLog> userLogList) {
        try {
            if (userLogList != null && !userLogList.isEmpty()) {
                // 先保存用户变更日志
                boolean success = uumsChangeUserLogService.saveBatch(userLogList);
                if (success) {
                    log.info("[SyncUumsUserScheduler] 成功保存 {} 条用户变更记录", userLogList.size());

                    // 处理每条用户变更记录
                    for (UumsChangeUserLog userLog : userLogList) {
                        try {
                            processUserOperation(userLog);
                        } catch (Exception e) {
                            log.error("[SyncUumsUserScheduler] 处理用户操作异常，用户名: {}, 变更类型: {}",
                                    userLog.getUsername(), userLog.getChangeType(), e);
                            // 更新日志记录的处理结果
                            updateUserLogResult(userLog, "同步失败", "0");
                        }
                    }
                } else {
                    log.error("[SyncUumsUserScheduler] 保存用户变更记录失败");
                }
            }
        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 保存用户变更记录异常", e);
        }
    }

    /**
     * 根据ChangeType处理用户操作
     */
    private void processUserOperation(UumsChangeUserLog userLog) throws Exception {
        String changeType = userLog.getChangeType();
        String username = userLog.getUsername();

        log.info("[SyncUumsUserScheduler] 开始处理用户操作，变更类型: {}, 用户名: {}", changeType, username);

        try {
            switch (changeType.toLowerCase()) {
                case "add":
                    handleAddUser(userLog);
                    break;
                case "update":
                    handleUpdateUser(userLog);
                    break;
                case "delete":
                    handleDeleteUser(userLog);
                    break;
                default:
                    log.warn("[SyncUumsUserScheduler] 未知的变更类型: {}", changeType);
                    updateUserLogResult(userLog, "同步失败：未知的变更类型", "0");
                    return;
            }

            log.info("[SyncUumsUserScheduler] 用户操作完成，变更类型: {}, 用户名: {}", changeType, username);

        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 用户操作异常，变更类型: {}, 用户名: {}", changeType, username, e);
            // 注意：具体的日志更新已在各个处理方法中完成，这里不再重复更新
            throw e;
        }
    }

    /**
     * 处理新增用户
     */
    private void handleAddUser(UumsChangeUserLog userLog) throws Exception {
        log.info("[SyncUumsUserScheduler] 处理新增用户，用户名: {}, 真实姓名: {}",
                userLog.getUsername(), userLog.getTruename());

        try {
            // 检查用户是否已存在
            SysUser existingUser = findUserByUsername(userLog.getUsername());
            if (existingUser != null) {
                log.warn("[SyncUumsUserScheduler] 用户已存在，用户名: {}, 标记为失败", userLog.getUsername());
                updateUserLogResult(userLog, "新增用户失败：用户已存在", "0");
                return;
            }

            // 根据currentOrgCode查找部门
            SysDepart department = findDepartByUumsOrgCode(userLog.getCurrentOrgcode());
            if (department == null) {
                log.warn("[SyncUumsUserScheduler] 未找到用户所属部门，组织代码: {}", userLog.getCurrentOrgcode());
                updateUserLogResult(userLog, "新增用户失败：未找到所属部门", "0");
                return;
            }

            // 构建新的SysUser对象
            SysUser newUser = createSysUserObject(userLog, department);
            if (newUser == null) {
                log.error("[SyncUumsUserScheduler] 创建SysUser对象失败");
                updateUserLogResult(userLog, "新增用户失败：创建用户对象失败", "0");
                return;
            }

            // 保存新用户
            saveUser(newUser);

            // 构建并保存SysUserDepart对象
            saveSysUserDepart(newUser.getId(), department.getId());

            // 保存默认角色ROLE_USER
            saveSysRole(newUser.getId());

            log.info("[SyncUumsUserScheduler] 成功新增用户 - 用户名: {}, 真实姓名: {}",
                    userLog.getUsername(), userLog.getTruename());

            // 新增成功，更新日志状态
            updateUserLogResult(userLog, "新增用户成功", "1");

        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 新增用户异常，用户名: {}", userLog.getUsername(), e);
            // 异常情况，更新日志状态为失败
            updateUserLogResult(userLog, "新增用户失败：" + e.getMessage(), "0");
            throw e;
        }
    }

    /**
     * 处理更新用户
     */
    private void handleUpdateUser(UumsChangeUserLog userLog) throws Exception {
        log.info("[SyncUumsUserScheduler] 处理更新用户，用户名: {}, 真实姓名: {}",
                userLog.getUsername(), userLog.getTruename());

        try {
            // 根据username查找现有用户
            SysUser existingUser = findUserByUsername(userLog.getUsername());
            if (existingUser == null) {
                log.warn("[SyncUumsUserScheduler] 未找到要更新的用户，用户名: {}", userLog.getUsername());
                updateUserLogResult(userLog, "更新用户失败：未找到目标用户", "0");
                return;
            }

            // 根据currentOrgCode查找新的部门
            SysDepart newDepartment = findDepartByUumsOrgCode(userLog.getCurrentOrgcode());
            if (newDepartment == null) {
                log.warn("[SyncUumsUserScheduler] 未找到用户新部门，组织代码: {}", userLog.getCurrentOrgcode());
                updateUserLogResult(userLog, "更新用户失败：未找到目标部门", "0");
                return;
            }

            // 更新用户信息
            updateUserInfo(existingUser, userLog, newDepartment);

            // 更新用户
            updateUser(existingUser);

            // 删除原有的用户部门关系
            deleteSysUserDepartByUserId(existingUser.getId());

            // 构建并保存新的SysUserDepart对象
            saveSysUserDepart(existingUser.getId(), newDepartment.getId());

            log.info("[SyncUumsUserScheduler] 成功更新用户 - 用户名: {}, 真实姓名: {}",
                    userLog.getUsername(), userLog.getTruename());

            // 更新成功，更新日志状态
            updateUserLogResult(userLog, "更新用户成功", "1");

        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 更新用户异常，用户名: {}", userLog.getUsername(), e);
            // 异常情况，更新日志状态为失败
            updateUserLogResult(userLog, "更新用户失败：" + e.getMessage(), "0");
            throw e;
        }
    }

    /**
     * 处理删除用户
     */
    private void handleDeleteUser(UumsChangeUserLog userLog) throws Exception {
        log.info("[SyncUumsUserScheduler] 处理删除用户，用户名: {}", userLog.getUsername());

        try {
            // 根据username查找要删除的用户
            SysUser existingUser = findUserByUsername(userLog.getUsername());
            if (existingUser == null) {
                log.warn("[SyncUumsUserScheduler] 未找到要删除的用户，用户名: {}", userLog.getUsername());
                updateUserLogResult(userLog, "删除用户失败：未找到目标用户", "0");
                return;
            }

            // 删除用户相关的所有关联数据
            deleteUserRelatedData(existingUser.getId());

            // 逻辑删除用户
            deleteUser(existingUser);

            log.info("[SyncUumsUserScheduler] 成功删除用户 - 用户名: {}", userLog.getUsername());

            // 删除成功，更新日志状态
            updateUserLogResult(userLog, "删除用户成功", "1");

        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 删除用户异常，用户名: {}", userLog.getUsername(), e);
            // 异常情况，更新日志状态为失败
            updateUserLogResult(userLog, "删除用户失败：" + e.getMessage(), "0");
            throw e;
        }
    }

    /**
     * 根据用户名查找用户
     */
    private SysUser findUserByUsername(String username) {
        try {
            if (sysUserService == null || oConvertUtils.isEmpty(username)) {
                return null;
            }

            QueryWrapper<SysUser> queryWrapper = new QueryWrapper<>();
            queryWrapper.eq("username", username);
            queryWrapper.eq("del_flag", CommonConstant.DEL_FLAG_0);

            return sysUserService.getOne(queryWrapper);
        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 查找用户异常，用户名: {}", username, e);
            return null;
        }
    }

    /**
     * 根据uumsOrgCode查找部门
     */
    private SysDepart findDepartByUumsOrgCode(String uumsOrgCode) {
        try {
            if (sysDepartService == null || oConvertUtils.isEmpty(uumsOrgCode)) {
                return null;
            }

            QueryWrapper<SysDepart> queryWrapper = new QueryWrapper<>();
            queryWrapper.eq("uums_org_code", uumsOrgCode);
            queryWrapper.eq("del_flag", CommonConstant.DEL_FLAG_0);

            return sysDepartService.getOne(queryWrapper);
        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 查找部门异常，uumsOrgCode: {}", uumsOrgCode, e);
            return null;
        }
    }

    /**
     * 创建SysUser对象
     */
    private SysUser createSysUserObject(UumsChangeUserLog userLog, SysDepart department) {
        try {
            SysUser sysUser = new SysUser();
            Date currentDate = new Date();

            // 设置基本信息
            sysUser.setUsername(userLog.getUsername());
            sysUser.setRealname(userLog.getTruename());

            // 设置工号
            if (oConvertUtils.isNotEmpty(userLog.getEmployeeNumber())) {
                sysUser.setWorkNo(userLog.getEmployeeNumber());
            }

            // 设置职位
            if (oConvertUtils.isNotEmpty(userLog.getPositionName())) {
                sysUser.setPost(userLog.getPositionName());
            }

            // 设置手机号
            if (oConvertUtils.isNotEmpty(userLog.getPreferredMobile())) {
                sysUser.setPhone(userLog.getPreferredMobile());
            }

            // 设置邮箱
            if (oConvertUtils.isNotEmpty(userLog.getEmail())) {
                sysUser.setEmail(userLog.getEmail());
            }

            // 设置组织编码（从部门获取）
            if (department != null) {
                sysUser.setOrgCode(department.getOrgCode());
            }

            // 设置密码相关
            String salt = oConvertUtils.randomGen(8);
            sysUser.setSalt(salt);
            // 设置默认密码为用户名
            String passwordEncode = PasswordUtil.encrypt(userLog.getUsername(), userLog.getUsername(), salt);
            sysUser.setPassword(passwordEncode);

            // 设置默认值
            sysUser.setStatus(CommonConstant.USER_UNFREEZE); // 启用状态
            sysUser.setDelFlag(CommonConstant.DEL_FLAG_0);
            sysUser.setCreateTime(currentDate);
            sysUser.setUpdateTime(currentDate);
            sysUser.setCreateBy("UUMS_SYNC");

            return sysUser;
        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 创建SysUser对象异常", e);
            return null;
        }
    }

    /**
     * 保存用户
     */
    private void saveUser(SysUser sysUser) throws Exception {
        sysUserService.save(sysUser);
    }

    /**
     * 更新用户
     */
    private void updateUser(SysUser sysUser) throws Exception {
        sysUserService.updateById(sysUser);
    }

    /**
     * 删除用户
     */
    private void deleteUser(SysUser sysUser) throws Exception {
        sysUser.setDelFlag(CommonConstant.DEL_FLAG_1);
        sysUser.setUpdateTime(new Date());
        sysUser.setUpdateBy("UUMS_SYNC");
        sysUserService.updateById(sysUser);
    }

    /**
     * 更新用户信息
     */
    private void updateUserInfo(SysUser existingUser, UumsChangeUserLog userLog, SysDepart department)
            throws Exception {
        Date currentDate = new Date();

        // 更新真实姓名
        if (oConvertUtils.isNotEmpty(userLog.getTruename())) {
            existingUser.setRealname(userLog.getTruename());
        }

        // 更新工号
        if (oConvertUtils.isNotEmpty(userLog.getEmployeeNumber())) {
            existingUser.setWorkNo(userLog.getEmployeeNumber());
        }

        // 更新职位
        if (oConvertUtils.isNotEmpty(userLog.getPositionName())) {
            existingUser.setPost(userLog.getPositionName());
        }

        // 更新手机号
        if (oConvertUtils.isNotEmpty(userLog.getPreferredMobile())) {
            existingUser.setPhone(userLog.getPreferredMobile());
        }

        // 更新邮箱
        if (oConvertUtils.isNotEmpty(userLog.getEmail())) {
            existingUser.setEmail(userLog.getEmail());
        }

        // 更新组织编码（从部门获取）
        if (department != null) {
            existingUser.setOrgCode(department.getOrgCode());
        }

        // 更新时间和操作人
        existingUser.setUpdateTime(currentDate);
        existingUser.setUpdateBy("UUMS_SYNC");
    }

    /**
     * 保存用户部门关系
     */
    private void saveSysUserDepart(String userId, String departId) throws Exception {
        SysUserDepart userDepart = new SysUserDepart(userId, departId);
        sysUserDepartService.save(userDepart);
    }

    /**
     * 根据用户ID删除用户部门关系
     */
    private void deleteSysUserDepartByUserId(String userId) throws Exception {
        QueryWrapper<SysUserDepart> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("user_id", userId);
        sysUserDepartService.remove(queryWrapper);
    }

    /**
     * 删除用户相关数据
     */
    private void deleteUserRelatedData(String userId) throws Exception {
        // 删除用户部门关系
        deleteSysUserDepartByUserId(userId);

        // 删除用户角色关系
        QueryWrapper<Object> userRoleWrapper = new QueryWrapper<>();
        userRoleWrapper.eq("user_id", userId);
        // 注意：这里需要根据实际的SysUserRole服务来删除，暂时用通用方式

        // 删除用户租户关系
        // 注意：这里需要根据实际的SysUserTenant服务来删除

        // 删除用户代理关系
        // 注意：这里需要根据实际的SysUserAgent服务来删除

        // 删除用户职位关系
        // 注意：这里需要根据实际的SysUserPosition服务来删除

        log.info("[SyncUumsUserScheduler] 删除用户相关数据完成，用户ID: {}", userId);
    }

    /**
     * 保存用户默认角色
     */
    private void saveSysRole(String userId) throws Exception {
        try {
            // 查询默认角色ROLE_USER
            QueryWrapper<SysRole> roleQueryWrapper = new QueryWrapper<>();
            roleQueryWrapper.eq("role_code", ROLE_USER);
            roleQueryWrapper.eq("del_flag", CommonConstant.DEL_FLAG_0);
            
            SysRole defaultRole = sysRoleService.getOne(roleQueryWrapper);
            if (defaultRole == null) {
                log.warn("[SyncUumsUserScheduler] 未找到默认角色ROLE_USER");
                return;
            }

            // 创建用户角色关系
            SysUserRole userRole = new SysUserRole(userId, defaultRole.getId());
            sysUserRoleService.save(userRole);

            log.info("[SyncUumsUserScheduler] 成功为用户分配默认角色ROLE_USER，用户ID: {}, 角色ID: {}", 
                    userId, defaultRole.getId());

        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 保存用户角色异常，用户ID: {}", userId, e);
            throw e;
        }
    }

    /**
     * 更新用户变更日志的处理结果
     */
    private void updateUserLogResult(UumsChangeUserLog userLog, String result, String resultFlag) {
        try {
            userLog.setResult(result);
            userLog.setResultFlag(resultFlag);
            userLog.setUpdateTime(new Date());

            // 更新数据库记录
            uumsChangeUserLogService.updateById(userLog);

            log.debug("[SyncUumsUserScheduler] 更新日志结果成功，用户名: {}, 结果: {}",
                    userLog.getUsername(), result);
        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 更新日志结果失败，用户名: {}", userLog.getUsername(), e);
        }
    }

    /**
     * 记录定时任务执行日志
     * 
     * @param startTime 任务开始时间
     * @param processedRecords 处理的记录数
     * @param success 是否执行成功
     */
    private void recordTaskExecutionLog(Date startTime, int processedRecords, boolean success) {
        try {
            String nodeIp = getNodeIpAddress();
            Date endTime = new Date();
            long executionTime = endTime.getTime() - startTime.getTime();
            
            String logContent = String.format(
                "UUMS用户同步定时任务执行完成 - 节点IP: %s, 处理记录数: %d, 执行耗时: %dms, 执行结果: %s, 开始时间: %s, 结束时间: %s",
                nodeIp, processedRecords, executionTime, 
                success ? "成功" : "失败",
                DateUtils.datetimeFormat.get().format(startTime),
                DateUtils.datetimeFormat.get().format(endTime)
            );
            
            // 使用BaseCommonService记录日志
            baseCommonService.addLog(logContent, CommonConstant.LOG_TYPE_2, CommonConstant.OPERATE_TYPE_3);
            
            log.info("[SyncUumsUserScheduler] 定时任务执行日志已记录");
            
        } catch (Exception e) {
            log.error("[SyncUumsUserScheduler] 记录定时任务执行日志异常", e);
        }
    }

    /**
     * 获取当前节点IP地址
     * 
     * @return 节点IP地址
     */
    private String getNodeIpAddress() {
        try {
            // 尝试从Spring上下文获取HttpServletRequest来获取IP
            HttpServletRequest request = SpringContextUtils.getHttpServletRequest();
            if (request != null) {
                return IpUtils.getIpAddr(request);
            }
        } catch (Exception e) {
            // 如果无法从请求获取IP，则获取本机IP
        }
        
        try {
            return java.net.InetAddress.getLocalHost().getHostAddress();
        } catch (Exception e) {
            log.warn("[SyncUumsUserScheduler] 获取节点IP地址失败", e);
            return "unknown";
        }
    }

}
