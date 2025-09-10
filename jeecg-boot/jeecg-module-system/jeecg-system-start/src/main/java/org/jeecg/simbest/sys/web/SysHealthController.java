package org.jeecg.simbest.sys.web;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.common.api.vo.Result;
import org.jeecg.config.shiro.IgnoreAuth;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

/**
 * 系统健康检查控制器
 * 
 * @author SIMBEST
 * @since 2025-08-02
 */
@Slf4j
@RestController
@RequestMapping("/sys/health")
@Tag(name = "系统健康检查")
public class SysHealthController {

    /**
     * 系统心跳检测接口
     * 提供匿名访问的健康状态检查，支持外部监控系统进行心跳检测
     * 
     * 使用场景：
     * - 负载均衡器健康检查
     * - 监控系统心跳检测
     * - 运维工具状态检查
     * 
     * 支持的HTTP方法：
     * - GET: 返回JSON格式的健康状态信息
     * - HEAD: 仅返回HTTP状态码，适用于简单的心跳检测
     * 
     * 访问示例：
     * GET  /sys/health/anonymous/heart
     * HEAD /sys/health/anonymous/heart
     * 
     * 响应格式：
     * GET请求：{"success": true, "message": "系统运行正常", "timestamp": 1693123456789}
     * HEAD请求：仅HTTP 200状态码
     */
    @IgnoreAuth
    @Operation(summary = "匿名心跳检测", description = "提供系统健康状态检查，支持GET和HEAD请求")
    @RequestMapping(value = "/anonymous/heart", method = {RequestMethod.GET, RequestMethod.HEAD})
    public Result<Object> anonymousHeartbeat() {
        try {
            // 记录心跳检测访问（仅在DEBUG级别，避免日志过多）
            log.debug("系统心跳检测被调用");
            
            // 可以在这里添加更复杂的健康检查逻辑
            // 比如检查数据库连接、Redis连接、关键服务状态等
            // 目前简单返回成功状态
            
            Result<Object> result = Result.ok("系统运行正常");
            result.setResult(System.currentTimeMillis()); // 返回时间戳作为响应数据
            return result;
            
        } catch (Exception e) {
            log.error("心跳检测异常: {}", e.getMessage(), e);
            return Result.error("系统异常");
        }
    }

    /**
     * 详细的系统健康状态检查（需要认证）
     * 提供更详细的系统状态信息，包括内存使用、线程数等
     * 
     * 访问示例：
     * GET /sys/health/status
     * 
     * 响应包含：
     * - JVM内存信息
     * - 活跃线程数
     * - 系统启动时间
     * - 当前时间戳
     */
    @Operation(summary = "系统状态检查", description = "获取详细的系统运行状态信息")
    @RequestMapping(value = "/status", method = RequestMethod.GET)
    public Result<Object> systemStatus() {
        try {
            // 获取系统运行信息
            Runtime runtime = Runtime.getRuntime();
            long totalMemory = runtime.totalMemory();
            long freeMemory = runtime.freeMemory();
            long usedMemory = totalMemory - freeMemory;
            long maxMemory = runtime.maxMemory();
            
            // 获取线程信息
            ThreadGroup rootGroup = Thread.currentThread().getThreadGroup();
            ThreadGroup parentGroup;
            while ((parentGroup = rootGroup.getParent()) != null) {
                rootGroup = parentGroup;
            }
            int activeThreads = rootGroup.activeCount();
            
            // 构建状态信息
            Result<Object> result = Result.ok("系统状态检查完成");
            
            // 系统状态数据
            java.util.Map<String, Object> statusData = new java.util.HashMap<>();
            statusData.put("timestamp", System.currentTimeMillis());
            statusData.put("uptime", System.currentTimeMillis() - 
                java.lang.management.ManagementFactory.getRuntimeMXBean().getStartTime());
            
            // JVM内存信息
            java.util.Map<String, Object> memoryInfo = new java.util.HashMap<>();
            memoryInfo.put("total", totalMemory);
            memoryInfo.put("used", usedMemory);
            memoryInfo.put("free", freeMemory);
            memoryInfo.put("max", maxMemory);
            memoryInfo.put("usagePercent", Math.round((double) usedMemory / totalMemory * 100));
            
            statusData.put("memory", memoryInfo);
            statusData.put("activeThreads", activeThreads);
            statusData.put("availableProcessors", runtime.availableProcessors());
            
            result.setResult(statusData);
            return result;
            
        } catch (Exception e) {
            log.error("系统状态检查异常: {}", e.getMessage(), e);
            return Result.error("获取系统状态失败");
        }
    }
}