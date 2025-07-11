package org.jeecg.modules.system.test;

import org.jeecg.JeecgSystemApplication;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

import javax.annotation.Resource;
import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.ResultSet;
import java.sql.Statement;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 数据库连接测试类
 * 验证数据库连接和基本查询功能
 */
@SpringBootTest(classes = JeecgSystemApplication.class)
@TestPropertySource(properties = {
    "spring.profiles.active=test"
})
public class DatabaseConnectionTest {

    @Resource
    private DataSource dataSource;

    @Test
    public void testDatabaseConnection() {
        System.out.println("=== 测试数据库连接 ===");
        
        try (Connection connection = dataSource.getConnection()) {
            assertNotNull(connection, "数据库连接不能为空");
            assertFalse(connection.isClosed(), "数据库连接应该是开启状态");
            
            DatabaseMetaData metaData = connection.getMetaData();
            System.out.println("数据库产品名称: " + metaData.getDatabaseProductName());
            System.out.println("数据库版本: " + metaData.getDatabaseProductVersion());
            System.out.println("驱动名称: " + metaData.getDriverName());
            System.out.println("驱动版本: " + metaData.getDriverVersion());
            
            System.out.println("✅ 数据库连接测试成功!");
        } catch (Exception e) {
            fail("数据库连接测试失败: " + e.getMessage());
        }
    }

    @Test
    public void testBasicQuery() {
        System.out.println("=== 测试基本查询功能 ===");
        
        try (Connection connection = dataSource.getConnection();
             Statement statement = connection.createStatement()) {
            
            // 测试基本查询
            String sql = "SELECT 1 as test_value";
            try (ResultSet rs = statement.executeQuery(sql)) {
                assertTrue(rs.next(), "查询结果应该有数据");
                assertEquals(1, rs.getInt("test_value"), "查询结果应该为1");
                System.out.println("✅ 基本查询测试成功!");
            }
            
        } catch (Exception e) {
            fail("基本查询测试失败: " + e.getMessage());
        }
    }

    @Test
    public void testDemoTableExists() {
        System.out.println("=== 测试demo表是否存在 ===");
        
        try (Connection connection = dataSource.getConnection();
             Statement statement = connection.createStatement()) {
            
            // 检查demo表是否存在
            String sql = "SELECT COUNT(*) as total FROM demo";
            try (ResultSet rs = statement.executeQuery(sql)) {
                assertTrue(rs.next(), "查询结果应该有数据");
                int count = rs.getInt("total");
                System.out.println("demo表记录数: " + count);
                assertTrue(count >= 0, "demo表应该存在且记录数>= 0");
                System.out.println("✅ demo表存在验证成功!");
            }
            
        } catch (Exception e) {
            fail("demo表验证失败: " + e.getMessage());
        }
    }

    @Test
    public void testDemoTableQuery() {
        System.out.println("=== 测试demo表查询 ===");
        
        try (Connection connection = dataSource.getConnection();
             Statement statement = connection.createStatement()) {
            
            // 查询demo表前3条记录
            String sql = "SELECT id, name, age FROM demo LIMIT 3";
            try (ResultSet rs = statement.executeQuery(sql)) {
                int recordCount = 0;
                while (rs.next()) {
                    recordCount++;
                    String id = rs.getString("id");
                    String name = rs.getString("name");
                    String age = rs.getString("age");
                    System.out.println("记录 " + recordCount + " - ID: " + id + ", 姓名: " + name + ", 年龄: " + age);
                }
                System.out.println("✅ demo表查询测试成功，共查询到 " + recordCount + " 条记录!");
            }
            
        } catch (Exception e) {
            fail("demo表查询测试失败: " + e.getMessage());
        }
    }
}