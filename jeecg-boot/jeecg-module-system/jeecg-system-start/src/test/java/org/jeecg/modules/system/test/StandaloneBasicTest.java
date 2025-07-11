package org.jeecg.modules.system.test;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 独立基础测试类 - 无需Spring Boot上下文
 * 确保CI环境下能够运行并生成测试报告
 */
public class StandaloneBasicTest {

    @Test
    public void testBasicMath() {
        System.out.println("=== 执行基础数学测试 ===");
        assertEquals(4, 2 + 2, "2 + 2 应该等于 4");
        assertEquals(6, 2 * 3, "2 * 3 应该等于 6");
        assertTrue(5 > 3, "5 应该大于 3");
        System.out.println("✅ 基础数学测试通过!");
    }

    @Test 
    public void testStringOperations() {
        System.out.println("=== 执行字符串测试 ===");
        String test = "JeecgBoot CI Test";
        assertNotNull(test, "字符串不应该为null");
        assertTrue(test.contains("CI"), "字符串应该包含'CI'");
        assertEquals(17, test.length(), "字符串长度应该是17");
        System.out.println("✅ 字符串测试通过!");
    }

    @Test
    public void testBooleanLogic() {
        System.out.println("=== 执行布尔逻辑测试 ===");
        assertTrue(true && true, "true && true 应该为 true");
        assertFalse(true && false, "true && false 应该为 false");
        assertTrue(true || false, "true || false 应该为 true");
        System.out.println("✅ 布尔逻辑测试通过!");
    }

    @Test
    public void testArrayOperations() {
        System.out.println("=== 执行数组测试 ===");
        int[] arr = {1, 2, 3, 4, 5};
        assertEquals(5, arr.length, "数组长度应该是5");
        assertEquals(1, arr[0], "第一个元素应该是1");
        assertEquals(5, arr[4], "最后一个元素应该是5");
        System.out.println("✅ 数组测试通过!");
    }
}