package org.jeecg.modules.system.test;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 纯JUnit测试 - 完全不依赖Spring Framework
 * 确保CI环境下能够正常运行基础测试
 */
public class PureJunitTest {

    @Test
    @DisplayName("基础断言测试")
    public void testBasicAssertion() {
        System.out.println("=== 执行纯JUnit基础测试 ===");
        assertTrue(true, "基础断言应该通过");
        assertEquals(2, 1 + 1, "1 + 1 应该等于 2");
        assertNotNull("test", "字符串不应该为空");
        System.out.println("✅ 纯JUnit基础测试通过!");
    }

    @Test
    @DisplayName("字符串操作测试")
    public void testStringOperations() {
        System.out.println("=== 执行字符串操作测试 ===");
        String str = "JeecgBoot";
        assertFalse(str.isEmpty(), "字符串不应该为空");
        assertTrue(str.length() > 0, "字符串长度应该大于0");
        assertEquals("JEECGBOOT", str.toUpperCase(), "大写转换应该正确");
        System.out.println("✅ 字符串测试通过!");
    }

    @Test
    @DisplayName("数学运算测试")
    public void testMathOperations() {
        System.out.println("=== 执行数学运算测试 ===");
        assertEquals(4, 2 * 2, "2 * 2 应该等于 4");
        assertEquals(5, 10 / 2, "10 / 2 应该等于 5");
        assertTrue(10 > 5, "10 应该大于 5");
        System.out.println("✅ 数学运算测试通过!");
    }

    @Test
    @DisplayName("CI环境验证测试")
    public void testCiEnvironment() {
        System.out.println("=== CI环境验证测试 ===");
        
        // 检查Java版本
        String javaVersion = System.getProperty("java.version");
        System.out.println("Java版本: " + javaVersion);
        assertNotNull(javaVersion, "Java版本不应该为空");
        
        // 检查操作系统
        String osName = System.getProperty("os.name");
        System.out.println("操作系统: " + osName);
        assertNotNull(osName, "操作系统名称不应该为空");
        
        // 检查当前工作目录
        String userDir = System.getProperty("user.dir");
        System.out.println("工作目录: " + userDir);
        assertNotNull(userDir, "工作目录不应该为空");
        
        System.out.println("✅ CI环境验证通过!");
    }
}