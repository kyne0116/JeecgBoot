package org.jeecg.config.mybatis;

import com.baomidou.mybatisplus.core.MybatisConfiguration;
import com.baomidou.mybatisplus.extension.plugins.MybatisPlusInterceptor;
import lombok.extern.slf4j.Slf4j;
import org.apache.ibatis.session.SqlSessionFactory;
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.config.BeanPostProcessor;
import org.springframework.stereotype.Component;

/**
 * 全局分页配置后处理器
 * 确保所有SqlSessionFactory都使用自定义分页插件
 * 
 * @author SIMBEST
 * @since 2025-08-26
 */
@Slf4j
@Component
public class GlobalPaginationConfig implements BeanPostProcessor {

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        if (bean instanceof SqlSessionFactory) {
            SqlSessionFactory sqlSessionFactory = (SqlSessionFactory) bean;
            log.info("=== 检测到SqlSessionFactory: {} ===", beanName);
            
            org.apache.ibatis.session.Configuration configuration = sqlSessionFactory.getConfiguration();
            
            // 检查是否已经有MyBatis Plus拦截器
            boolean hasPaginationInterceptor = configuration.getInterceptors().stream()
                    .anyMatch(interceptor -> 
                        interceptor instanceof MybatisPlusInterceptor ||
                        interceptor.getClass().getSimpleName().contains("Pagination"));
                        
            if (!hasPaginationInterceptor) {
                log.warn(">>> SqlSessionFactory {} 缺少分页拦截器，正在添加自定义分页插件", beanName);
                
                // 创建自定义分页插件并添加到配置中
                MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
                CustomPaginationInnerInterceptor paginationInterceptor = new CustomPaginationInnerInterceptor();
                interceptor.addInnerInterceptor(paginationInterceptor);
                
                configuration.addInterceptor(interceptor);
                log.info(">>> 已为SqlSessionFactory {} 添加自定义分页插件", beanName);
            } else {
                log.info(">>> SqlSessionFactory {} 已经包含分页拦截器", beanName);
            }
            
            // 打印所有拦截器信息用于调试
            log.info(">>> SqlSessionFactory {} 拦截器列表:", beanName);
            configuration.getInterceptors().forEach(interceptor -> {
                log.info("    - {}", interceptor.getClass().getSimpleName());
            });
        }
        
        return bean;
    }
}