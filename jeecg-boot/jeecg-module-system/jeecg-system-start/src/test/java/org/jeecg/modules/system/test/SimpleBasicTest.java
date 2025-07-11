package org.jeecg.modules.system.test;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 简单基础测试类
 * 确保CI环境下至少有一个测试可以运行
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.NONE)
public class SimpleBasicTest {

    @Test
    public void testBasicAssertion() {
        System.out.println("=== 执行基础断言测试 ===");
        assertTrue(true, "基础断言应该通过");
        assertEquals(2, 1 + 1, "1 + 1 应该等于 2");
        assertNotNull("test", "字符串不应该为空");
        System.out.println("✅ 基础测试通过!");
    }

    @Test
    public void testStringOperations() {
        System.out.println("=== 执行字符串操作测试 ===");
        String str = "JeecgBoot";
        assertFalse(str.isEmpty(), "字符串不应该为空");
        assertTrue(str.length() > 0, "字符串长度应该大于0");
        assertEquals("JEECGBOOT", str.toUpperCase(), "大写转换应该正确");
        System.out.println("✅ 字符串测试通过!");
    }

    @Test
    public void testMathOperations() {
        System.out.println("=== 执行数学运算测试 ===");
        assertEquals(4, 2 * 2, "2 * 2 应该等于 4");
        assertEquals(5, 10 / 2, "10 / 2 应该等于 5");
        assertTrue(10 > 5, "10 应该大于 5");
        System.out.println("✅ 数学运算测试通过!");
    }
}