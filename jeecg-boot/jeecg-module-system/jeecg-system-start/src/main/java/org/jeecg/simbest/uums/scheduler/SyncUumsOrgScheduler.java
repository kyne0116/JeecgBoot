package org.jeecg.simbest.uums.scheduler;

import static org.jeecg.simbest.constants.SimbestConstants.APPCODE_UUMS;
import static org.jeecg.simbest.constants.SimbestConstants.OAUTH2_UUMS;
import static org.jeecg.simbest.constants.SimbestConstants.UUMS_SYNC_ORG;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

import jakarta.servlet.http.HttpServletRequest;
import org.jeecg.common.constant.CommonConstant;
import org.jeecg.common.util.DateUtils;
import org.jeecg.common.util.IpUtils;
import org.jeecg.common.util.RestUtil;
import org.jeecg.common.util.SpringContextUtils;
import org.jeecg.common.util.oConvertUtils;
import org.jeecg.modules.base.service.BaseCommonService;
import org.jeecg.simbest.config.AppConfig;
import org.jeecg.simbest.token.SimbestAppToken;
import org.jeecg.simbest.uums.entity.UumsChangeOrgLog;
import org.jeecg.simbest.uums.service.IUumsChangeOrgLogService;
import org.jeecg.simbest.utils.DistributedLockUtil;
import org.jeecg.modules.system.entity.SysDepart;
import org.jeecg.modules.system.service.ISysDepartService;
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

@Slf4j
@Component
public class SyncUumsOrgScheduler {

    @Autowired
    private AppConfig appConfig;

    @Autowired
    private IUumsChangeOrgLogService uumsChangeOrgLogService;

    @Autowired
    private ISysDepartService sysDepartService;

    @Autowired
    private DistributedLockUtil distributedLockUtil;

    @Autowired
    private BaseCommonService baseCommonService;

    /**
     * 定时同步UUMS组织数据
     * Cron表达式通过配置文件 jeecg.uums.scheduler.org-sync-cron 配置
     * 默认每天凌晨1点执行：0 0 1 * * ?
     */
    @Scheduled(cron = "${jeecg.uums.scheduler.org-sync-cron:0 0 1 * * ?}")
    public void syncUumsOrgs() {
        String lockKey = "sync_uums_orgs";
        String lockValue = null;
        
        try {
            // 尝试获取分布式锁
            lockValue = distributedLockUtil.acquireLock(lockKey, 30);
            
            if (lockValue != null) {
                String uumsAddress = appConfig.getUumsAddress();
                log.info("[SyncUumsOrgScheduler] 获取分布式锁成功，定时任务开始执行 - UUMS系统地址: {}", uumsAddress);
                
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
                
                log.info("[SyncUumsOrgScheduler] 同步时间范围: {} ~ {}", startDate, endDate);
                syncUumsOrgs(startDate, endDate);
                
                log.info("[SyncUumsOrgScheduler] 定时任务执行完成");
            } else {
                log.info("[SyncUumsOrgScheduler] 未获取到分布式锁，其他节点正在执行同步任务，跳过本次执行");
                return;
            }
        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 定时任务执行异常", e);
        } finally {
            // 释放分布式锁
            if (lockValue != null) {
                distributedLockUtil.releaseLock(lockKey, lockValue);
            }
        }
    }

    /**
     * 同步UUMS组织变更数据
     *
     * @param startDate 开始日期
     * @param endDate   结束日期
     * @return 处理的记录数
     */
    public int syncUumsOrgs(String startDate, String endDate) {
        Date taskStartTime = new Date();
        int processedRecords = 0;
        boolean success = false;
        
        try {
            String uumsAddress = appConfig.getUumsAddress();
            log.info("[SyncUumsOrgScheduler] 开始同步组织数据 - UUMS系统地址: {}, 时间范围: {} ~ {}",
                    uumsAddress, startDate, endDate);
    
            // 1. 获取访问令牌
            SimbestAppToken.TokenResponse tokenResponse = SimbestAppToken.getAccessToken(
                    APPCODE_UUMS, uumsAddress + OAUTH2_UUMS);
    
            if (tokenResponse == null || tokenResponse.getAccessToken() == null) {
                log.error("[SyncUumsOrgScheduler] 获取访问令牌失败");
                return 0;
            }
    
            log.info("[SyncUumsOrgScheduler] 成功获取访问令牌");
    
            // 2. 构建请求参数
            JSONObject requestParams = buildRequestParams(startDate, endDate);
            log.info("[SyncUumsOrgScheduler] 请求参数: {}", requestParams.toJSONString());
    
            // 3. 发送HTTP请求
            String requestUrl = uumsAddress + UUMS_SYNC_ORG;
            ResponseEntity<JSONObject> response = sendHttpRequest(requestUrl, requestParams,
                    tokenResponse.getAccessToken());
    
            if (response == null || response.getBody() == null) {
                log.error("[SyncUumsOrgScheduler] HTTP请求失败，响应为空");
                return 0;
            }
    
            JSONObject responseBody = response.getBody();
            log.info("[SyncUumsOrgScheduler] 接收到响应: {}", responseBody.toJSONString());
    
            // 4. 处理响应数据
            processedRecords = processResponse(responseBody);
            success = true;
            
            return processedRecords;
    
        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 同步组织数据异常", e);
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

            log.info("[SyncUumsOrgScheduler] 发送POST请求到: {}", url);

            // 发送POST请求
            return RestUtil.request(url, HttpMethod.POST, headers, null, params, JSONObject.class);

        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 发送HTTP请求异常: {}", e.getMessage(), e);
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
                log.error("[SyncUumsOrgScheduler] 接口返回错误，errcode: {}, message: {}",
                        errcode, responseBody.getString("message"));
                return 0;
            }

            log.info("[SyncUumsOrgScheduler] 接口调用成功: {}", responseBody.getString("message"));

            // 获取数据部分
            JSONObject data = responseBody.getJSONObject("data");
            if (data == null) {
                log.warn("[SyncUumsOrgScheduler] 响应中没有data字段");
                return 0;
            }

            Integer totalNum = data.getInteger("totalNum");
            String findDataDate = data.getString("findDataDate");
            log.info("[SyncUumsOrgScheduler] 获取到组织变更数据，总数: {}, 查询时间: {}", totalNum, findDataDate);

            // 获取详细数据列表
            com.alibaba.fastjson.JSONArray details = data.getJSONArray("details");
            if (details == null || details.isEmpty()) {
                log.info("[SyncUumsOrgScheduler] 没有组织变更数据");
                return 0;
            }

            // 转换并保存数据
            List<UumsChangeOrgLog> orgLogList = convertToOrgLogList(details, findDataDate);
            saveOrgLogList(orgLogList);

            log.info("[SyncUumsOrgScheduler] 成功处理 {} 条组织变更记录", orgLogList.size());
            return orgLogList.size();

        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 处理响应数据异常", e);
            return 0;
        }
    }

    /**
     * 将JSON数组转换为UumsChangeOrgLog对象列表
     */
    private List<UumsChangeOrgLog> convertToOrgLogList(com.alibaba.fastjson.JSONArray details, String syncDate) {
        List<UumsChangeOrgLog> orgLogList = new ArrayList<>();
        Date currentDate = new Date();

        for (int i = 0; i < details.size(); i++) {
            try {
                JSONObject detail = details.getJSONObject(i);

                // 将JSON对象转换为UumsChangeOrgLog实体
                UumsChangeOrgLog orgLog = new UumsChangeOrgLog();

                // 设置基础字段
                orgLog.setCreateTime(currentDate);
                orgLog.setUpdateTime(currentDate);
                orgLog.setSyncDate(currentDate);

                // 映射UUMS返回的字段到实体字段
                orgLog.setChangeType(detail.getString("CHANGETYPE"));
                orgLog.setPreOrgname(detail.getString("PREORGNAME"));
                orgLog.setOrgname(detail.getString("ORGNAME"));
                orgLog.setOrgcode(detail.getString("ORGCODE"));
                orgLog.setOrgtype(detail.getString("ORGTYPE"));
                orgLog.setParentOrgname(detail.getString("PARENTORGNAME"));
                orgLog.setParentOrgcode(detail.getString("PARENTORGCODE"));
                orgLog.setDisplayName(detail.getString("DISPLAYNAME"));
                orgLog.setDisplayOrder(detail.getInteger("DISPLAYORDER"));

                // 设置20位组织代码（如果有的话）
                String oldTxlOrgCode = detail.getString("OLDTXLORGCODE");
                if (oldTxlOrgCode != null && !oldTxlOrgCode.isEmpty()) {
                    orgLog.setOrgcode20(oldTxlOrgCode);
                }

                String oldTxlParentOrgCode = detail.getString("OLDTXLPARENTORGCODE");
                if (oldTxlParentOrgCode != null && !oldTxlParentOrgCode.isEmpty()) {
                    orgLog.setParentOrgcode20(oldTxlParentOrgCode);
                }

                // 设置状态和结果
                orgLog.setResult("同步成功");
                orgLog.setResultFlag("1"); // 成功标志

                orgLogList.add(orgLog);

            } catch (Exception e) {
                log.error("[SyncUumsOrgScheduler] 转换第{}条记录异常: {}", i, e.getMessage(), e);
            }
        }

        return orgLogList;
    }

    /**
     * 批量保存组织变更日志并同步到JeecgBoot部门
     */
    private void saveOrgLogList(List<UumsChangeOrgLog> orgLogList) {
        try {
            if (orgLogList != null && !orgLogList.isEmpty()) {
                // 1. 先保存组织变更日志
                boolean success = uumsChangeOrgLogService.saveBatch(orgLogList);
                if (success) {
                    log.info("[SyncUumsOrgScheduler] 成功保存 {} 条组织变更记录", orgLogList.size());

                    // 2. 根据ChangeType处理JeecgBoot部门操作
                    for (UumsChangeOrgLog orgLog : orgLogList) {
                        try {
                            processDepartmentOperation(orgLog);
                        } catch (Exception e) {
                            log.error("[SyncUumsOrgScheduler] 处理部门操作异常，组织代码: {}, 变更类型: {}",
                                    orgLog.getOrgcode(), orgLog.getChangeType(), e);
                            // 更新日志记录的处理结果
                            updateOrgLogResult(orgLog, "同步失败", "0");
                        }
                    }
                } else {
                    log.error("[SyncUumsOrgScheduler] 保存组织变更记录失败");
                }
            }
        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 保存组织变更记录异常", e);
        }
    }

    /**
     * 根据ChangeType处理部门操作
     */
    private void processDepartmentOperation(UumsChangeOrgLog orgLog) throws Exception {
        String changeType = orgLog.getChangeType();
        String orgCode = orgLog.getOrgcode();

        log.info("[SyncUumsOrgScheduler] 开始处理部门操作，变更类型: {}, 组织代码: {}", changeType, orgCode);

        try {
            switch (changeType.toLowerCase()) {
                case "add":
                    handleAddDepartment(orgLog);
                    break;
                case "update":
                    handleUpdateDepartment(orgLog);
                    break;
                case "delete":
                    handleDeleteDepartment(orgLog);
                    break;
                default:
                    log.warn("[SyncUumsOrgScheduler] 未知的变更类型: {}", changeType);
                    updateOrgLogResult(orgLog, "同步失败：未知的变更类型", "0");
                    return;
            }

            log.info("[SyncUumsOrgScheduler] 部门操作完成，变更类型: {}, 组织代码: {}", changeType, orgCode);

        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 部门操作异常，变更类型: {}, 组织代码: {}", changeType, orgCode, e);
            // 注意：具体的日志更新已在各个处理方法中完成，这里不再重复更新
            throw e;
        }
    }

    /**
     * 处理新增部门
     */
    private void handleAddDepartment(UumsChangeOrgLog orgLog) throws Exception {
        log.info("[SyncUumsOrgScheduler] 处理新增部门，组织代码: {}, 组织名称: {}",
                orgLog.getOrgcode(), orgLog.getOrgname());

        try {
            // 直接使用注入的ISysDepartService
            if (sysDepartService == null) {
                log.error("[SyncUumsOrgScheduler] sysDepartService未正确注入，跳过新增部门操作");
                updateOrgLogResult(orgLog, "新增部门失败：服务未正确注入", "0");
                return;
            }

            // 1. 检查部门是否已存在（根据uumsOrgCode）
            SysDepart existingDepart = findDepartByUumsOrgCode(orgLog.getOrgcode());
            if (existingDepart != null) {
                log.warn("[SyncUumsOrgScheduler] 部门已存在，组织代码: {}, 跳过新增操作", orgLog.getOrgcode());
                // 根据业务需求，部门已存在可以标记为成功（避免重复创建）
                updateOrgLogResult(orgLog, "新增部门成功：部门已存在", "1");
                return;
            }

            // 2. 查找父部门
            String parentId = null;
            if (oConvertUtils.isNotEmpty(orgLog.getParentOrgcode())) {
                SysDepart parentDepart = findDepartByUumsOrgCode(orgLog.getParentOrgcode());
                if (parentDepart != null) {
                    parentId = parentDepart.getId();
                    log.info("[SyncUumsOrgScheduler] 找到父部门，父组织代码: {}, 父部门ID: {}",
                            orgLog.getParentOrgcode(), parentId);
                } else {
                    log.warn("[SyncUumsOrgScheduler] 未找到父部门，父组织代码: {}", orgLog.getParentOrgcode());
                }
            }

            // 3. 构建新的SysDepart对象
            SysDepart newDepart = createSysDepartObject(orgLog, parentId);
            if (newDepart == null) {
                log.error("[SyncUumsOrgScheduler] 创建SysDepart对象失败");
                updateOrgLogResult(orgLog, "新增部门失败：创建部门对象失败", "0");
                return;
            }

            // 4. 保存新部门
            saveDepartment(newDepart);
            log.info("[SyncUumsOrgScheduler] 成功新增部门 - 组织代码: {}, 组织名称: {}",
                    orgLog.getOrgcode(), orgLog.getOrgname());

            // 新增成功，更新日志状态
            updateOrgLogResult(orgLog, "新增部门成功", "1");

        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 新增部门异常，组织代码: {}", orgLog.getOrgcode(), e);
            // 异常情况，更新日志状态为失败
            updateOrgLogResult(orgLog, "新增部门失败：" + e.getMessage(), "0");
            throw e;
        }
    }

    /**
     * 处理更新部门
     */
    private void handleUpdateDepartment(UumsChangeOrgLog orgLog) throws Exception {
        log.info("[SyncUumsOrgScheduler] 处理更新部门，组织代码: {}, 组织名称: {}",
                orgLog.getOrgcode(), orgLog.getOrgname());

        try {
            // 直接使用注入的ISysDepartService
            if (sysDepartService == null) {
                log.error("[SyncUumsOrgScheduler] sysDepartService未正确注入，跳过更新部门操作");
                updateOrgLogResult(orgLog, "更新部门失败：服务未正确注入", "0");
                return;
            }

            // 1. 根据uumsOrgCode查找现有部门
            SysDepart existingDepart = findDepartByUumsOrgCode(orgLog.getOrgcode());
            if (existingDepart == null) {
                log.warn("[SyncUumsOrgScheduler] 未找到要更新的部门，组织代码: {}", orgLog.getOrgcode());
                updateOrgLogResult(orgLog, "更新部门失败：未找到目标部门", "0");
                return;
            }

            // 2. 查找新的父部门
            String newParentId = null;
            if (oConvertUtils.isNotEmpty(orgLog.getParentOrgcode())) {
                SysDepart parentDepart = findDepartByUumsOrgCode(orgLog.getParentOrgcode());
                if (parentDepart != null) {
                    newParentId = parentDepart.getId();
                    log.info("[SyncUumsOrgScheduler] 找到新父部门，父组织代码: {}, 父部门ID: {}",
                            orgLog.getParentOrgcode(), newParentId);
                } else {
                    log.warn("[SyncUumsOrgScheduler] 未找到新父部门，父组织代码: {}", orgLog.getParentOrgcode());
                }
            }

            // 3. 更新部门信息
            updateDepartmentInfo(existingDepart, orgLog, newParentId);

            // 4. 保存更新
            updateDepartment(existingDepart);
            log.info("[SyncUumsOrgScheduler] 成功更新部门 - 组织代码: {}, 组织名称: {}",
                    orgLog.getOrgcode(), orgLog.getOrgname());

            // 更新成功，更新日志状态
            updateOrgLogResult(orgLog, "更新部门成功", "1");

        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 更新部门异常，组织代码: {}", orgLog.getOrgcode(), e);
            // 异常情况，更新日志状态为失败
            updateOrgLogResult(orgLog, "更新部门失败：" + e.getMessage(), "0");
            throw e;
        }
    }

    /**
     * 处理删除部门
     */
    private void handleDeleteDepartment(UumsChangeOrgLog orgLog) throws Exception {
        log.info("[SyncUumsOrgScheduler] 处理删除部门，组织代码: {}, 组织名称: {}",
                orgLog.getOrgcode(), orgLog.getOrgname());

        try {
            // 直接使用注入的ISysDepartService
            if (sysDepartService == null) {
                log.error("[SyncUumsOrgScheduler] sysDepartService未正确注入，跳过删除部门操作");
                updateOrgLogResult(orgLog, "删除部门失败：服务未正确注入", "0");
                return;
            }

            // 1. 根据uumsOrgCode查找要删除的部门
            SysDepart existingDepart = findDepartByUumsOrgCode(orgLog.getOrgcode());
            if (existingDepart == null) {
                log.warn("[SyncUumsOrgScheduler] 未找到要删除的部门，组织代码: {}", orgLog.getOrgcode());
                updateOrgLogResult(orgLog, "删除部门失败：未找到目标部门", "0");
                return;
            }

            // 2. 进行逻辑删除
            deleteDepartment(existingDepart);
            log.info("[SyncUumsOrgScheduler] 成功删除部门 - 组织代码: {}, 组织名称: {}",
                    orgLog.getOrgcode(), orgLog.getOrgname());

            // 删除成功，更新日志状态
            updateOrgLogResult(orgLog, "删除部门成功", "1");

        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 删除部门异常，组织代码: {}", orgLog.getOrgcode(), e);
            // 异常情况，更新日志状态为失败
            updateOrgLogResult(orgLog, "删除部门失败：" + e.getMessage(), "0");
            throw e;
        }
    }

    /**
     * 根据uumsOrgCode查找部门
     */
    private SysDepart findDepartByUumsOrgCode(String uumsOrgCode) {
        try {
            if (sysDepartService == null) {
                return null;
            }

            // 使用QueryWrapper查询
            QueryWrapper<SysDepart> queryWrapper = new QueryWrapper<>();
            queryWrapper.eq("uums_org_code", uumsOrgCode);
            queryWrapper.eq("del_flag", CommonConstant.DEL_FLAG_0);

            // 调用service的getOne方法
            return sysDepartService.getOne(queryWrapper);
        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 查找部门异常，uumsOrgCode: {}", uumsOrgCode, e);
            return null;
        }
    }

    /**
     * 创建SysDepart对象
     */
    private SysDepart createSysDepartObject(UumsChangeOrgLog orgLog, String parentId) {
        try {
            // 直接创建SysDepart对象
            SysDepart sysDepart = new SysDepart();
            Date currentDate = new Date();

            // 设置基本信息
            sysDepart.setDepartName(orgLog.getOrgname());
            sysDepart.setUumsOrgCode(orgLog.getOrgcode());
            sysDepart.setUumsParentOrgCode(orgLog.getParentOrgcode());

            // 设置父部门ID
            if (oConvertUtils.isNotEmpty(parentId)) {
                sysDepart.setParentId(parentId);
            }

            // 设置显示信息（优先使用displayName）
            if (oConvertUtils.isNotEmpty(orgLog.getDisplayName())) {
                sysDepart.setDepartName(orgLog.getDisplayName());
            }
            if (orgLog.getDisplayOrder() != null) {
                sysDepart.setDepartOrder(orgLog.getDisplayOrder());
            }

            // 设置组织类型
            if (oConvertUtils.isNotEmpty(orgLog.getOrgtype())) {
                sysDepart.setOrgType(orgLog.getOrgtype());
            }

            // 设置默认值
            sysDepart.setStatus("1"); // 启用状态
            sysDepart.setDelFlag(CommonConstant.DEL_FLAG_0.toString());
            sysDepart.setCreateTime(currentDate);
            sysDepart.setUpdateTime(currentDate);
            sysDepart.setCreateBy("UUMS_SYNC");

            // 设置组织类别：如果有父部门则为2（组织机构），否则为1（公司）
            String orgCategory = oConvertUtils.isEmpty(parentId) ? "1" : "2";
            sysDepart.setOrgCategory(orgCategory);

            return sysDepart;
        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 创建SysDepart对象异常", e);
            return null;
        }
    }

    /**
     * 保存部门
     */
    private void saveDepartment(SysDepart sysDepart) throws Exception {
        // 调用saveDepartData方法
        sysDepartService.saveDepartData(sysDepart, "UUMS_SYNC");
    }

    /**
     * 更新部门信息
     */
    private void updateDepartmentInfo(SysDepart existingDepart, UumsChangeOrgLog orgLog, String newParentId)
            throws Exception {
        Date currentDate = new Date();

        // 更新部门名称
        if (oConvertUtils.isNotEmpty(orgLog.getOrgname())) {
            existingDepart.setDepartName(orgLog.getOrgname());
        }

        // 更新显示名称（优先使用displayName）
        if (oConvertUtils.isNotEmpty(orgLog.getDisplayName())) {
            existingDepart.setDepartName(orgLog.getDisplayName());
        }

        // 更新显示顺序
        if (orgLog.getDisplayOrder() != null) {
            existingDepart.setDepartOrder(orgLog.getDisplayOrder());
        }

        // 更新父部门ID
        if (newParentId != null) {
            existingDepart.setParentId(newParentId);
        }

        // 更新UUMS相关字段
        existingDepart.setUumsOrgCode(orgLog.getOrgcode());
        existingDepart.setUumsParentOrgCode(orgLog.getParentOrgcode());

        // 更新时间和操作人
        existingDepart.setUpdateTime(currentDate);
        existingDepart.setUpdateBy("UUMS_SYNC");
    }

    /**
     * 更新部门
     */
    private void updateDepartment(SysDepart sysDepart) throws Exception {
        // 调用updateDepartDataById方法
        sysDepartService.updateDepartDataById(sysDepart, "UUMS_SYNC");
    }

    /**
     * 删除部门
     */
    private void deleteDepartment(SysDepart sysDepart) throws Exception {
        // 获取部门ID
        String departId = sysDepart.getId();

        // 调用deleteDepart方法进行逻辑删除
        sysDepartService.deleteDepart(departId);
    }

    /**
     * 更新组织变更日志的处理结果
     */
    private void updateOrgLogResult(UumsChangeOrgLog orgLog, String result, String resultFlag) {
        try {
            orgLog.setResult(result);
            orgLog.setResultFlag(resultFlag);
            orgLog.setUpdateTime(new Date());

            // 更新数据库记录
            uumsChangeOrgLogService.updateById(orgLog);

            log.debug("[SyncUumsOrgScheduler] 更新日志结果成功，组织代码: {}, 结果: {}",
                    orgLog.getOrgcode(), result);
        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 更新日志结果失败，组织代码: {}", orgLog.getOrgcode(), e);
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
                "UUMS组织同步定时任务执行完成 - 节点IP: %s, 处理记录数: %d, 执行耗时: %dms, 执行结果: %s, 开始时间: %s, 结束时间: %s",
                nodeIp, processedRecords, executionTime, 
                success ? "成功" : "失败",
                DateUtils.datetimeFormat.get().format(startTime),
                DateUtils.datetimeFormat.get().format(endTime)
            );
            
            // 使用BaseCommonService记录日志
            baseCommonService.addLog(logContent, CommonConstant.LOG_TYPE_2, CommonConstant.OPERATE_TYPE_3);
            
            log.info("[SyncUumsOrgScheduler] 定时任务执行日志已记录");
            
        } catch (Exception e) {
            log.error("[SyncUumsOrgScheduler] 记录定时任务执行日志异常", e);
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
            log.warn("[SyncUumsOrgScheduler] 获取节点IP地址失败", e);
            return "unknown";
        }
    }

}
