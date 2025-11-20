package org.jeecg.config.mybatis;

import com.baomidou.mybatisplus.annotation.DbType;
import com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor;
import com.baomidou.mybatisplus.extension.plugins.pagination.DialectFactory;
import com.baomidou.mybatisplus.extension.plugins.pagination.dialects.IDialect;
import lombok.extern.slf4j.Slf4j;
import org.apache.ibatis.executor.Executor;

import java.sql.Connection;

/**
 * 自定义分页插件，专门处理OceanBase Oracle兼容模式
 * 解决OceanBase在Oracle兼容模式下分页SQL语法不兼容问题
 *
 * @author SIMBEST
 * @since 2025-08-26
 */
@Slf4j
public class CustomPaginationInnerInterceptor extends PaginationInnerInterceptor {

    /**
     * 查找数据库方言，针对OceanBase Oracle兼容模式进行特殊处理
     *
     * @param executor MyBatis执行器
     * @return IDialect 数据库方言实现
     */
    @Override
    protected IDialect findIDialect(Executor executor) {
        try {
            Connection conn = executor.getTransaction().getConnection();
            String jdbcUrl = conn.getMetaData().getURL();
            String databaseProductName = conn.getMetaData().getDatabaseProductName();

            log.info("=== 自定义分页插件方言检测 ===");
            log.info("数据库连接URL: {}", jdbcUrl);
            log.info("数据库产品名称: {}", databaseProductName);

            // 针对OceanBase Oracle兼容模式特殊处理
            if (jdbcUrl.contains(":oceanbase:oracle:") ||
                (jdbcUrl.contains(":oceanbase:") && jdbcUrl.contains("oracle"))) {
                log.info(">>> 检测到OceanBase Oracle兼容模式，强制使用Oracle分页方言");
                IDialect oracleDialect = DialectFactory.getDialect(DbType.ORACLE);
                log.info(">>> 返回Oracle方言实现: {}", oracleDialect.getClass().getSimpleName());
                return oracleDialect;
            }

            // 标准Oracle处理
            if (jdbcUrl.contains(":oracle:")) {
                log.debug("检测到Oracle数据库，使用Oracle分页方言");
                return DialectFactory.getDialect(DbType.ORACLE);
            }

            // 其他数据库使用父类默认处理
            IDialect dialect = super.findIDialect(executor);
            log.info(">>> 使用默认方言处理: {}", dialect.getClass().getSimpleName());
            return dialect;

        } catch (Exception e) {
            log.warn("获取数据库方言失败，使用默认OTHER方言: {}", e.getMessage());
            return DialectFactory.getDialect(DbType.OTHER);
        }
    }

    /**
     * 获取数据库类型描述，用于调试日志
     *
     * @param jdbcUrl JDBC连接URL
     * @return 数据库类型描述
     */
    private String getDbTypeDescription(String jdbcUrl) {
        if (jdbcUrl.contains(":oceanbase:oracle:")) {
            return "OceanBase Oracle兼容模式";
        } else if (jdbcUrl.contains(":oceanbase:")) {
            return "OceanBase MySQL兼容模式";
        } else if (jdbcUrl.contains(":oracle:")) {
            return "Oracle数据库";
        } else if (jdbcUrl.contains(":mysql:")) {
            return "MySQL数据库";
        } else {
            return "未知数据库类型";
        }
    }
}
