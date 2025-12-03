package org.jeecg.modules.copyright.agent.impl;

import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.agent.core.*;
import org.jeecg.modules.copyright.agent.tools.PoiWordUtil;
import org.jeecg.modules.copyright.vo.CopyrightRequirement;
import org.jeecg.modules.copyright.vo.FormValidationResult;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * ReactFormFillAgent - 软著信息采集表填报Agent
 * <p>
 * 根据需求信息自动填充Word格式的软著信息采集表
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Component
@Slf4j
public class ReactFormFillAgent implements CopyrightAgent {

    @Autowired
    private ChatModel chatModel;

    @Autowired
    private PoiWordUtil poiWordUtil;

    private static final String AGENT_INSTRUCTION = """
            你是一个专业的软著申报表格填报助手。你的任务是根据用户提供的需求信息,
            自动填充《软著信息采集表》Word文档。

            表格字段说明:
            1. 软件全称 - 完整的软件名称
            2. 软件简称 - 软件的简称或缩写
            3. 版本号 - 软件版本号(如V1.0)
            4. 软件分类 - 应用软件/系统软件/支撑软件/嵌入式软件
            5. 编程语言 - 主要使用的编程语言
            6. 技术架构 - 技术栈和架构说明
            7. 功能列表 - 软件的核心功能(至少3项)
            8. 申请人信息 - 申请人姓名/单位名称
            9. 联系方式 - 联系人和电话

            填报要求:
            1. 所有必填字段必须填写完整
            2. 功能列表需要详细列出,每项功能独立成行
            3. 日期格式统一为"yyyy年MM月dd日"
            4. 确保信息准确无误,与需求一致

            工作流程:
            1. 接收用户需求信息
            2. 验证必填字段完整性
            3. 调用POI工具填充Word文档
            4. 验证填充结果
            5. 返回生成的表格文件路径
            """;

    @Override
    @LogAgentExecution
    public AgentResult execute(AgentContext context) {
        log.info("[ReactFormFillAgent] 开始执行表格填报, sessionId: {}", context.getSessionId());

        try {
            CopyrightRequirement requirement = context.getRequirement();
            if (requirement == null) {
                return AgentResult.failure("需求信息不能为空");
            }

            // 验证模板文件是否存在
            if (!poiWordUtil.validateTemplate()) {
                log.warn("[ReactFormFillAgent] Word模板文件不存在,将跳过表格填充");
                return AgentResult.failure("Word模板文件不存在,请先准备模板文件");
            }

            // 验证必填字段
            FormValidationResult validationResult = validateRequirement(requirement, context.getSessionId());
            if (!validationResult.getIsValid()) {
                log.warn("[ReactFormFillAgent] 需求信息验证失败: {}", validationResult.getValidationErrors());
                return AgentResult.failure("需求信息验证失败: " + String.join(", ", validationResult.getValidationErrors()));
            }

            // 填充Word文档
            String filePath = poiWordUtil.fillCopyrightInfoForm(requirement, context.getSessionId());

            // 构建验证结果
            FormValidationResult result = FormValidationResult.builder()
                    .isValid(true)
                    .missingFields(new ArrayList<>())
                    .validationErrors(new ArrayList<>())
                    .filePath(filePath)
                    .sessionId(context.getSessionId())
                    .build();

            log.info("[ReactFormFillAgent] 表格填报完成, 文件路径: {}", filePath);

            return AgentResult.success("表格填报完成", result);

        } catch (Exception e) {
            log.error("[ReactFormFillAgent] 表格填报失败", e);
            return AgentResult.failure("表格填报失败: " + e.getMessage());
        }
    }

    /**
     * 验证需求信息完整性
     */
    private FormValidationResult validateRequirement(CopyrightRequirement requirement, String sessionId) {
        List<String> missingFields = new ArrayList<>();
        List<String> validationErrors = new ArrayList<>();

        // 检查必填字段
        if (requirement.getSoftwareName() == null || requirement.getSoftwareName().isEmpty()) {
            missingFields.add("软件全称");
        }
        if (requirement.getShortName() == null || requirement.getShortName().isEmpty()) {
            missingFields.add("软件简称");
        }
        if (requirement.getVersion() == null || requirement.getVersion().isEmpty()) {
            missingFields.add("版本号");
        }
        if (requirement.getCategory() == null || requirement.getCategory().isEmpty()) {
            missingFields.add("软件分类");
        }
        if (requirement.getCodeLanguage() == null || requirement.getCodeLanguage().isEmpty()) {
            missingFields.add("编程语言");
        }
        if (requirement.getTechStack() == null || requirement.getTechStack().isEmpty()) {
            missingFields.add("技术架构");
        }
        if (requirement.getFeatures() == null || requirement.getFeatures().isEmpty()) {
            missingFields.add("功能列表");
        } else if (requirement.getFeatures().size() < 3) {
            validationErrors.add("功能列表至少需要3项功能,当前只有" + requirement.getFeatures().size() + "项");
        }
        if (requirement.getApplicant() == null || requirement.getApplicant().getName() == null || requirement.getApplicant().getName().isEmpty()) {
            missingFields.add("申请人信息");
        }

        boolean isValid = missingFields.isEmpty() && validationErrors.isEmpty();

        return FormValidationResult.builder()
                .isValid(isValid)
                .missingFields(missingFields)
                .validationErrors(validationErrors)
                .sessionId(sessionId)
                .build();
    }

    /**
     * 构建ReactAgent实例(当前版本不需要工具函数,直接调用POI)
     */
    @SuppressWarnings("unused")
    private ReactAgent buildReactAgent(AgentContext context) {
        log.info("[ReactFormFillAgent] 开始构建ReactAgent");

        // 当前版本不需要额外的工具函数,直接使用POI填充
        ReactAgent agent = (ReactAgent) ReactAgent.builder()
                .name("ReactFormFillAgent")
                .description("软著信息采集表填报Agent,自动填充Word文档")
                .instruction(AGENT_INSTRUCTION)
                .model(chatModel)
                .build();

        log.info("[ReactFormFillAgent] ReactAgent构建完成");
        return agent;
    }

    @Override
    public String getAgentName() {
        return "ReactFormFillAgent";
    }

    @Override
    public AgentType getAgentType() {
        return AgentType.REACT_AGENT;
    }
}
