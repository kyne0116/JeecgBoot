package org.jeecg;

import com.xkcoding.justauth.autoconfigure.JustAuthAutoConfiguration;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.common.util.oConvertUtils;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.ImportAutoConfiguration;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.mongo.MongoAutoConfiguration;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.core.env.Environment;
import org.springframework.scheduling.annotation.EnableAsync;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
* 单体启动类（采用此类启动为单体模式）
* 报错提醒: 未集成mongo报错，可以打开启动类上面的注释 exclude={MongoAutoConfiguration.class}
*/
@Slf4j
@EnableAsync
@SpringBootApplication(exclude = MongoAutoConfiguration.class)
@ImportAutoConfiguration(JustAuthAutoConfiguration.class)  // spring boot 3.x justauth 兼容性处理
public class JeecgSystemApplication extends SpringBootServletInitializer {

    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder application) {
        return application.sources(JeecgSystemApplication.class);
    }

    public static void main(String[] args) throws UnknownHostException {
        // 强制加载OceanBase驱动类
        try {
            Class.forName("com.oceanbase.jdbc.Driver");
            log.info("[JEECG] OceanBase JDBC Driver loaded successfully");
        } catch (ClassNotFoundException e) {
            log.warn("[JEECG] OceanBase JDBC Driver not found: " + e.getMessage());
        }

        SpringApplication app = new SpringApplication(JeecgSystemApplication.class);
        Map<String, Object> defaultProperties = new HashMap<>();
        defaultProperties.put("management.health.elasticsearch.enabled", false);
        app.setDefaultProperties(defaultProperties);
        log.info("[JEECG] Elasticsearch Health Check Enabled: false");

        ConfigurableApplicationContext application = app.run(args);
        Environment env = application.getEnvironment();

        // 打印系统配置信息
        printSystemInfo(env);

        // 打印访问地址信息
        printAccessInfo(env);

    }

    /**
     * 打印系统配置信息
     */
    private static void printSystemInfo(Environment env) {
        String[] activeProfiles = env.getActiveProfiles();
        String dataSourceUrl = env.getProperty("spring.datasource.dynamic.datasource.master.url");
        String redisInfo = getRedisInfo(env);
        String uumsAddress = env.getProperty("jeecg.uums.address");

        log.info("\n========================================" +
                "\n系统配置信息:" +
                "\n激活Profile: " + Arrays.toString(activeProfiles) +
                "\n数据库连接: " + (dataSourceUrl != null ? dataSourceUrl : "未配置") +
                "\n" + redisInfo +
                "\nUUMS地址: " + (uumsAddress != null ? uumsAddress : "未配置") +
                "\n========================================");
    }

    /**
     * 获取Redis配置信息
     * 注意: Spring Boot 3.x 使用 spring.data.redis.* 前缀
     */
    private static String getRedisInfo(Environment env) {
        // Spring Boot 3.x 前缀
        final String PREFIX = "spring.data.redis.";

        // 首先检查集群模式配置
        String clusterNodesProperty = env.getProperty(PREFIX + "cluster.nodes");

        // 如果没有找到cluster.nodes，尝试从数组格式读取
        if (clusterNodesProperty == null || clusterNodesProperty.isEmpty()) {
            StringBuilder nodeBuilder = new StringBuilder();
            int index = 0;
            String node;
            while ((node = env.getProperty(PREFIX + "cluster.nodes[" + index + "]")) != null) {
                if (index > 0) {
                    nodeBuilder.append(",");
                }
                nodeBuilder.append(node);
                index++;
            }
            if (nodeBuilder.length() > 0) {
                clusterNodesProperty = nodeBuilder.toString();
            }
        }

        if (clusterNodesProperty != null && !clusterNodesProperty.isEmpty()) {
            String password = env.getProperty(PREFIX + "password");
            String timeout = env.getProperty(PREFIX + "timeout");
            String maxRedirects = env.getProperty(PREFIX + "cluster.max-redirects");

            StringBuilder redisInfo = new StringBuilder();
            redisInfo.append("Redis集群: 集群模式");

            // 解析集群节点
            String[] nodes = clusterNodesProperty.split(",");
            redisInfo.append("\n集群节点: (共").append(nodes.length).append("个节点)");

            for (int i = 0; i < nodes.length; i++) {
                String node = nodes[i].trim();
                if (i == nodes.length - 1) {
                    redisInfo.append("\n  └─ ").append(node);
                } else {
                    redisInfo.append("\n  ├─ ").append(node);
                }
            }

            redisInfo.append("\n认证密码: ").append(password != null && !password.isEmpty() ? "已配置" : "未配置");
            redisInfo.append("\n连接超时: ").append(timeout != null ? timeout : "默认");
            redisInfo.append("\n最大重定向: ").append(maxRedirects != null ? maxRedirects : "3");

            return redisInfo.toString();
        } else {
            // 单机模式或无Redis配置
            String redisHost = env.getProperty(PREFIX + "host");
            String redisPort = env.getProperty(PREFIX + "port");
            String redisDatabase = env.getProperty(PREFIX + "database");
            String password = env.getProperty(PREFIX + "password");

            // 检查是否有任何Redis配置
            if (redisHost == null && redisPort == null && redisDatabase == null && password == null) {
                return "Redis服务: 未配置 (测试环境)";
            }

            return "Redis服务: " +
                    (redisHost != null ? redisHost + ":" + (redisPort != null ? redisPort : "6379") : "未配置") +
                    " (DB:" + (redisDatabase != null ? redisDatabase : "0") + ")" +
                    " 密码:" + (password != null && !password.isEmpty() ? "已配置" : "未配置");
        }
    }

    /**
     * 打印访问地址信息
     */
    private static void printAccessInfo(Environment env) throws UnknownHostException {
        String ip = InetAddress.getLocalHost().getHostAddress();
        String port = env.getProperty("server.port");
        String path = oConvertUtils.getString(env.getProperty("server.servlet.context-path"));

        log.info("\n----------------------------------------------------------\n\t" +
                "Application Jeecg-Boot is running! Access URLs:\n\t" +
                "Local: \t\thttp://localhost:" + port + path + "\n\t" +
                "External: \thttp://" + ip + ":" + port + path + "/doc.html\n\t" +
                "Swagger文档: \thttp://" + ip + ":" + port + path + "/doc.html\n" +
                "----------------------------------------------------------");
    }

}