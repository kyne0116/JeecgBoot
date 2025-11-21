package org.jeecg.simbest.config;

import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

import lombok.Data;

/**
 * 应用配置统一管理类
 * 用于统一收敛和管理SpringBoot配置变量
 * 其他类不直接使用@Value注解，而是通过注入AppConfig实例来获取配置值
 *
 * @author: jeecg-boot
 */
@Slf4j
@Data
@Configuration
public class AppConfig {

    /**
     * 应用编码
     */
    @Value("${spring.application.name:jeecg-app}")
    private String appcode;

    /**
     * UUMS系统地址
     */
    @Value("${jeecg.uums.address:}")
    private String uumsAddress;

    /**
     * UUMS组织同步定时任务Cron表达式
     */
    @Value("${jeecg.uums.scheduler.org-sync-cron:0 0 1 * * ?}")
    private String uumsOrgSyncCron;

    /**
     * UUMS用户同步定时任务Cron表达式
     */
    @Value("${jeecg.uums.scheduler.user-sync-cron:0 0 2 * * ?}")
    private String uumsUserSyncCron;

    @PostConstruct
    public void init() {
        log.info("************************************应用配置START**************************************************");
        log.info("应用编码【{}】", appcode);
        log.info("主数据地址【{}】", uumsAddress);
        log.info("UUMS组织同步Cron【{}】", uumsOrgSyncCron);
        log.info("UUMS用户同步Cron【{}】", uumsUserSyncCron);
        log.info("####################################应用配置END##################################################");
        log.info("");
    }

    /**
     * 获取UUMS系统地址
     *
     * @return UUMS系统地址
     */
    public String getUumsAddress() {
        return uumsAddress;
    }

    /**
     * 获取UUMS组织同步定时任务Cron表达式
     *
     * @return Cron表达式
     */
    public String getUumsOrgSyncCron() {
        return uumsOrgSyncCron;
    }

    /**
     * 获取UUMS用户同步定时任务Cron表达式
     *
     * @return Cron表达式
     */
    public String getUumsUserSyncCron() {
        return uumsUserSyncCron;
    }


}
