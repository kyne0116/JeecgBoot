package org.jeecg.modules.copyright.agent.tools;

import cn.hutool.json.JSONUtil;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.vo.CopyrightRequirement;
import org.jeecg.modules.copyright.vo.ExtractDataRequest;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.model.ToolContext;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.function.BiFunction;

/**
 * 结构化数据提取工具
 * 从对话历史中提取结构化的软著申报信息JSON
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Component
@Slf4j
public class ExtractDataTool implements BiFunction<ExtractDataRequest, ToolContext, CopyrightRequirement> {

    public static final String DEFAULT_TOOL_DESCRIPTION =
            "从多轮对话内容中提取结构化的软著申报信息,转换为标准JSON格式,包含所有必填字段";

    @Autowired
    private ChatModel chatModel;

    @Override
    public CopyrightRequirement apply(ExtractDataRequest request, ToolContext context) {
        log.info("[工具函数] extractStructuredData 被调用, sessionId: {}", request.getSessionId());
        log.debug("[工具函数] 对话内容长度: {} 字符", request.getConversationText().length());

        try {
            // 构建提取Prompt
            String extractPrompt = buildExtractPrompt(request.getConversationText());

            // 调用LLM提取结构化数据
            Prompt prompt = new Prompt(extractPrompt);
            ChatResponse chatResponse = chatModel.call(prompt);
            String jsonContent = chatResponse.getResult().getOutput().getText();

            log.info("[工具函数] LLM提取的JSON长度: {} 字符", jsonContent.length());
            log.debug("[工具函数] 提取的JSON: {}", jsonContent);

            // 清理JSON字符串(去除Markdown代码块标记)
            String cleanedJson = cleanJsonString(jsonContent);

            // 解析为CopyrightRequirement对象
            CopyrightRequirement requirement = parseRequirement(cleanedJson);

            log.info("[工具函数] extractStructuredData 执行成功: softwareName={}",
                    requirement.getSoftwareName());

            return requirement;

        } catch (Exception e) {
            log.error("[工具函数] extractStructuredData 执行失败", e);
            // 返回空对象,让Agent继续对话
            return CopyrightRequirement.builder()
                    .softwareName("提取失败,请用户重新提供信息")
                    .build();
        }
    }

    /**
     * 构建数据提取Prompt
     */
    private String buildExtractPrompt(String conversationText) {
        return String.format("""
                你是一个专业的信息提取专家。请从以下对话内容中提取软著申报信息,并严格按照JSON格式输出。

                对话内容:
                %s

                请提取以下信息并转换为JSON格式:
                1. softwareName: 软件全称
                2. shortName: 软件简称
                3. version: 版本号
                4. category: 软件分类(应用软件/系统软件/支撑软件/嵌入式软件)
                5. codeLanguage: 主要编程语言
                6. techStack: 技术架构
                7. features: 核心功能列表(数组,每个功能包含name和description)
                8. innovations: 技术创新点列表(字符串数组)
                9. architecture: 系统架构描述
                10. applicant: 申请人信息(包含name和type字段)
                11. devCompleteDate: 开发完成日期(yyyy-MM-dd格式)

                输出格式示例:
                {
                  "softwareName": "XXX管理系统",
                  "shortName": "XXX系统",
                  "version": "v1.0",
                  "category": "应用软件",
                  "codeLanguage": "Java",
                  "techStack": "Spring Boot + Vue3",
                  "features": [
                    {"name": "用户管理", "description": "支持用户增删改查"},
                    {"name": "数据统计", "description": "实时数据分析"}
                  ],
                  "innovations": ["微服务架构", "AI智能推荐"],
                  "architecture": "前后端分离架构",
                  "applicant": {"name": "XX公司", "type": "enterprise"},
                  "devCompleteDate": "2025-12-01"
                }

                要求:
                1. 只输出JSON,不要有任何其他文字
                2. 如果某个字段对话中未提及,设为空字符串""或空数组[]
                3. features数组中每个功能必须包含name和description
                4. applicant.type只能是"enterprise"或"individual"
                """, conversationText);
    }

    /**
     * 清理JSON字符串
     */
    private String cleanJsonString(String jsonContent) {
        // 去除Markdown代码块标记
        String cleaned = jsonContent.trim();
        if (cleaned.startsWith("```json")) {
            cleaned = cleaned.substring(7);
        } else if (cleaned.startsWith("```")) {
            cleaned = cleaned.substring(3);
        }
        if (cleaned.endsWith("```")) {
            cleaned = cleaned.substring(0, cleaned.length() - 3);
        }
        return cleaned.trim();
    }

    /**
     * 解析JSON为CopyrightRequirement对象
     */
    private CopyrightRequirement parseRequirement(String jsonString) {
        try {
            return JSONUtil.toBean(jsonString, CopyrightRequirement.class);
        } catch (Exception e) {
            log.error("[工具函数] JSON解析失败: {}", jsonString, e);
            throw new RuntimeException("JSON解析失败: " + e.getMessage());
        }
    }
}
