package org.jeecg.modules.copyright.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * Copyright模块配置类
 * 启用AOP和异步支持
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Configuration
@EnableAspectJAutoProxy  // 启用AOP
@EnableAsync             // 启用异步支持
public class CopyrightModuleConfig {

    // 其他配置Bean将在后续添加
}
