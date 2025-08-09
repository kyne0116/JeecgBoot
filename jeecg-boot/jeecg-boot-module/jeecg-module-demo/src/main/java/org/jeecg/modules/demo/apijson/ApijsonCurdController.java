package org.jeecg.modules.demo.apijson;

import org.jeecg.common.api.vo.Result;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

// 使用阿里巴巴的JSONObject替代，因为apijson.JSONObject不存在
import com.alibaba.fastjson.JSONObject;

// APIJSON 特有包导入验证 - 验证jar包是否成功引入
import apijson.JSONRequest;
import apijson.JSONResponse;
import apijson.StringUtil;
import lombok.extern.slf4j.Slf4j;

/**
 * APIJSON CRUD 测试控制器
 * 用于验证APIJSON依赖包是否成功引入和编译通过
 * 
 * @author JeecgBoot
 * @since 2025-08-09
 */
@Slf4j
@RestController
@RequestMapping("/demo/apijson")
public class ApijsonCurdController {

    /**
     * 综合测试APIJSON核心类导入
     * 验证多个APIJSON包的导入成功
     */
    @PostMapping("/testComprehensive")
    public Result<?> testComprehensive(@RequestBody(required = false) String requestBody) {
        log.info("=== APIJSON 综合测试开始 ===");

        try {
            // 1. 验证JSONRequest类导入
            Class<?> jsonRequestClass = JSONRequest.class;
            log.info("✅ JSONRequest 类导入成功: {}", jsonRequestClass.getName());

            // 2. 验证JSONResponse类导入
            Class<?> jsonResponseClass = JSONResponse.class;
            log.info("✅ JSONResponse 类导入成功: {}", jsonResponseClass.getName());

            // 3. 测试StringUtil工具类
            boolean hasRequestBody = StringUtil.isNotEmpty(requestBody);
            log.info("✅ StringUtil 使用成功，请求体是否为空: {}", !hasRequestBody);

            // 4. 构建测试结果
            JSONObject testResult = new JSONObject();
            testResult.put("jsonRequestTest", "✅ 类导入成功");
            testResult.put("jsonResponseTest", "✅ 类导入成功");
            testResult.put("stringUtilTest", "✅ 工具类使用成功");
            testResult.put("jsonRequestClassName", jsonRequestClass.getName());
            testResult.put("jsonResponseClassName", jsonResponseClass.getName());
            testResult.put("overallStatus", "🎉 APIJSON 依赖包验证成功");

            // 5. 如果有请求体，测试JSON解析
            if (hasRequestBody) {
                JSONObject requestJson = JSONObject.parseObject(requestBody);
                testResult.put("requestData", requestJson);
                testResult.put("jsonParseTest", "✅ JSON解析成功");
                log.info("✅ JSON 解析成功");
            } else {
                testResult.put("jsonParseTest", "⚠️ 跳过(无请求体)");
            }

            log.info("🎉 APIJSON 综合测试全部通过！");
            return Result.ok(testResult);

        } catch (Exception e) {
            log.error("❌ APIJSON 综合测试失败", e);
            return Result.error("APIJSON 综合测试失败: " + e.getMessage());
        }
    }

}
