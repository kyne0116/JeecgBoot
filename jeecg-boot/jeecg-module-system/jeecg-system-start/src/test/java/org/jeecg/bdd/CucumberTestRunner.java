package org.jeecg.bdd;

import org.junit.platform.suite.api.*;

import static io.cucumber.junit.platform.engine.Constants.*;

/**
 * Cucumber BDD测试运行器
 * 用于执行基于Gherkin语法的测试场景
 */
@Suite
@IncludeEngines("cucumber")
@SelectClasspathResource("features")
@ConfigurationParameter(key = PLUGIN_PROPERTY_NAME, 
    value = "html:target/cucumber-reports/html," +
            "json:target/cucumber-reports/json/cucumber.json," +
            "junit:target/cucumber-reports/xml/cucumber.xml," +
            "pretty")
@ConfigurationParameter(key = GLUE_PROPERTY_NAME, value = "org.jeecg.bdd")
@ConfigurationParameter(key = FEATURES_PROPERTY_NAME, value = "src/test/resources/features")
@ConfigurationParameter(key = EXECUTION_DRY_RUN_PROPERTY_NAME, value = "false")
@ConfigurationParameter(key = PLUGIN_PUBLISH_ENABLED_PROPERTY_NAME, value = "false")
public class CucumberTestRunner {
    // 测试运行器类，无需实现任何方法
    // Cucumber会自动扫描features目录下的.feature文件
    // 并执行对应的步骤定义
}