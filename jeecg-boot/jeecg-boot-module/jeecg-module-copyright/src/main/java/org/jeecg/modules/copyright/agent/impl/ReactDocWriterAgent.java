package org.jeecg.modules.copyright.agent.impl;

import cn.hutool.json.JSONUtil;
import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.agent.core.*;
import org.jeecg.modules.copyright.agent.tools.MarkdownToWordConverter;
import org.jeecg.modules.copyright.vo.CopyrightRequirement;
import org.jeecg.modules.copyright.vo.DocumentValidationResult;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * ReactDocWriterAgent - 申报说明文档撰写Agent
 * <p>
 * 基于需求自动生成3000-5000字的软著申报说明文档
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Component
@Slf4j
public class ReactDocWriterAgent implements CopyrightAgent {

    @Autowired
    private ChatModel chatModel;

    @Autowired
    private MarkdownToWordConverter markdownToWordConverter;

    private static final int MIN_WORD_COUNT = 3000;
    private static final int MAX_WORD_COUNT = 5000;

    private static final String AGENT_INSTRUCTION = """
            你是一个专业的软著申报文档撰写专家。你的任务是根据软著申报需求,
            撰写一份3000-5000字的专业申报说明文档。

            文档结构要求:
            1. 软件概述(500-800字)
               - 软件基本信息
               - 软件定位和应用场景
               - 目标用户群体
            2. 功能说明(1200-1500字)
               - 详细描述每个核心功能
               - 功能的实现原理
               - 功能的使用场景
            3. 技术架构(800-1000字)
               - 系统架构设计
               - 技术选型说明
               - 关键技术实现
            4. 技术创新点(600-800字)
               - 详细阐述每个创新点
               - 创新点的技术优势
               - 与同类产品的对比
            5. 应用价值(400-600字)
               - 社会价值
               - 经济价值
               - 技术价值

            撰写要求:
            1. 内容专业、严谨、详实
            2. 突出技术创新和应用价值
            3. 字数控制在3000-5000字之间
            4. 使用规范的技术术语
            5. 逻辑清晰,层次分明

            格式要求:
            1. 使用Markdown格式编写
            2. 章节使用#、##、###标记
            3. 列表使用-或数字标记
            4. 最终转换为仿宋12号字的Word文档
            """;

    @Override
    @LogAgentExecution
    public AgentResult execute(AgentContext context) {
        log.info("[ReactDocWriterAgent] 开始执行文档撰写, sessionId: {}", context.getSessionId());

        try {
            CopyrightRequirement requirement = context.getRequirement();
            if (requirement == null) {
                return AgentResult.failure("需求信息不能为空");
            }

            // 生成Markdown文档内容
            String markdownContent = generateMarkdownDocument(requirement);

            // 统计字数
            int wordCount = markdownToWordConverter.countChineseCharacters(markdownContent);
            log.info("[ReactDocWriterAgent] 文档字数: {}", wordCount);

            // 验证字数是否符合要求
            boolean meetsWordCount = wordCount >= MIN_WORD_COUNT && wordCount <= MAX_WORD_COUNT;

            // 验证章节完整性
            List<String> missingSections = validateSections(markdownContent);
            boolean sectionsComplete = missingSections.isEmpty();

            // 转换为Word文档
            String filePath = markdownToWordConverter.convertMarkdownToWord(
                    markdownContent, context.getSessionId());

            // 构建验证结果
            DocumentValidationResult result = DocumentValidationResult.builder()
                    .isValid(meetsWordCount && sectionsComplete)
                    .wordCount(wordCount)
                    .meetsWordCountRequirement(meetsWordCount)
                    .sectionsComplete(sectionsComplete)
                    .missingSections(missingSections)
                    .filePath(filePath)
                    .markdownContent(markdownContent)
                    .sessionId(context.getSessionId())
                    .build();

            log.info("[ReactDocWriterAgent] 文档撰写完成 - 字数:{}, 符合要求:{}, 文件路径:{}",
                    wordCount, result.getIsValid(), filePath);

            return AgentResult.success("文档撰写完成", result);

        } catch (Exception e) {
            log.error("[ReactDocWriterAgent] 文档撰写失败", e);
            return AgentResult.failure("文档撰写失败: " + e.getMessage());
        }
    }

    /**
     * 生成Markdown格式的申报说明文档
     * TODO: 实际应该由LLM生成,当前为模拟实现
     */
    private String generateMarkdownDocument(CopyrightRequirement requirement) {
        StringBuilder sb = new StringBuilder();

        // 文档标题
        sb.append("# ").append(requirement.getSoftwareName()).append("申报说明文档\n\n");

        // 1. 软件概述
        sb.append("## 一、软件概述\n\n");
        sb.append("### 1.1 软件基本信息\n\n");
        sb.append("软件全称:").append(requirement.getSoftwareName()).append("\n\n");
        sb.append("软件简称:").append(requirement.getShortName()).append("\n\n");
        sb.append("版本号:").append(requirement.getVersion()).append("\n\n");
        sb.append("软件分类:").append(requirement.getCategory()).append("\n\n");
        sb.append("主要编程语言:").append(requirement.getCodeLanguage()).append("\n\n");
        sb.append("技术架构:").append(requirement.getTechStack()).append("\n\n");

        sb.append("### 1.2 软件定位\n\n");
        sb.append(requirement.getSoftwareName()).append("是一款专业的").append(requirement.getCategory())
                .append(",采用").append(requirement.getTechStack()).append("架构开发,")
                .append("为用户提供高效、稳定、易用的解决方案。本软件面向企业用户和个人用户,")
                .append("致力于解决实际业务场景中的关键问题,提升工作效率,降低运营成本。\n\n");

        sb.append("### 1.3 应用场景\n\n");
        sb.append("本软件广泛应用于各类企业和组织,适用于日常业务管理、数据处理、信息查询等多个场景。")
                .append("通过先进的技术手段和友好的用户界面,帮助用户快速完成各项任务,显著提升业务处理能力。\n\n");

        // 2. 功能说明
        sb.append("## 二、功能说明\n\n");
        if (requirement.getFeatures() != null && !requirement.getFeatures().isEmpty()) {
            for (int i = 0; i < requirement.getFeatures().size(); i++) {
                CopyrightRequirement.SoftwareFeature feature = requirement.getFeatures().get(i);
                sb.append("### 2.").append(i + 1).append(" ").append(feature.getName()).append("\n\n");
                sb.append("该功能模块提供了").append(feature.getName()).append("的完整解决方案。")
                        .append("通过系统化的流程设计和智能化的处理机制,实现了业务操作的自动化和智能化。")
                        .append("用户可以通过简单的界面操作,快速完成").append(feature.getName()).append("相关的各项任务,")
                        .append("大幅提升工作效率。系统采用先进的算法和优化技术,确保功能执行的高性能和高可靠性。\n\n");
            }
        }

        sb.append("各功能模块之间相互配合,形成完整的业务闭环,为用户提供一站式服务体验。")
                .append("系统支持灵活的配置和扩展,可根据不同用户的实际需求进行定制化调整。\n\n");

        // 3. 技术架构
        sb.append("## 三、技术架构\n\n");
        sb.append("### 3.1 系统架构设计\n\n");
        sb.append("本软件采用").append(requirement.getTechStack()).append("架构,实现了前后端分离、")
                .append("模块化设计、分布式部署等先进的架构模式。系统分为表现层、业务逻辑层、数据访问层和数据存储层,")
                .append("各层职责清晰,松耦合设计,便于维护和扩展。\n\n");

        sb.append("### 3.2 技术选型\n\n");
        sb.append("系统主要采用").append(requirement.getCodeLanguage()).append("作为开发语言,")
                .append("结合").append(requirement.getTechStack()).append("技术栈,")
                .append("实现了高性能、高可用、高扩展性的系统架构。数据库采用关系型数据库,")
                .append("支持复杂的数据查询和事务处理。系统还集成了缓存技术、消息队列等中间件,")
                .append("提升系统的整体性能和可靠性。\n\n");

        sb.append("### 3.3 关键技术实现\n\n");
        sb.append("系统采用了多项关键技术来保证系统的稳定运行和高效执行。")
                .append("包括但不限于:数据加密技术保障信息安全,负载均衡技术提升系统处理能力,")
                .append("缓存技术加速数据访问,异步处理技术提升用户体验等。")
                .append("这些技术的综合应用,确保了系统能够应对各种复杂场景和高并发访问需求。\n\n");

        // 4. 技术创新点
        sb.append("## 四、技术创新点\n\n");
        if (requirement.getInnovations() != null && !requirement.getInnovations().isEmpty()) {
            for (int i = 0; i < requirement.getInnovations().size(); i++) {
                String innovation = requirement.getInnovations().get(i);
                sb.append("### 4.").append(i + 1).append(" ").append(innovation).append("\n\n");
                sb.append("本软件在").append(innovation).append("方面实现了重要突破。")
                        .append("通过创新的技术手段和独特的设计思路,解决了传统方案存在的诸多问题,")
                        .append("显著提升了系统的性能和用户体验。该创新点具有较高的技术难度,")
                        .append("在同类产品中处于领先地位,为用户带来了实实在在的价值。\n\n");
            }
        }

        sb.append("以上技术创新点充分体现了本软件的技术优势和竞争力,")
                .append("为软件的持续发展和市场拓展奠定了坚实基础。\n\n");

        // 5. 应用价值
        sb.append("## 五、应用价值\n\n");
        sb.append("### 5.1 社会价值\n\n");
        sb.append("本软件的推广应用,有助于提升行业整体的信息化水平,推动业务流程优化和管理模式创新。")
                .append("通过提供高效便捷的解决方案,帮助用户节省时间成本,提高工作质量,")
                .append("为社会创造更多价值。\n\n");

        sb.append("### 5.2 经济价值\n\n");
        sb.append("软件的应用能够有效降低企业运营成本,提升业务处理效率,增强市场竞争力。")
                .append("通过自动化和智能化的手段,减少人工投入,降低错误率,创造可观的经济效益。\n\n");

        sb.append("### 5.3 技术价值\n\n");
        sb.append("本软件采用的创新技术和架构设计,对行业技术发展具有重要的参考和借鉴价值。")
                .append("系统的成功实施,验证了相关技术方案的可行性和有效性,")
                .append("为后续技术演进和产品迭代提供了宝贵经验。\n\n");

        return sb.toString();
    }

    /**
     * 验证章节完整性
     */
    private List<String> validateSections(String markdownContent) {
        List<String> missingSections = new ArrayList<>();

        if (!markdownContent.contains("## 一、软件概述") && !markdownContent.contains("## 软件概述")) {
            missingSections.add("软件概述");
        }
        if (!markdownContent.contains("## 二、功能说明") && !markdownContent.contains("## 功能说明")) {
            missingSections.add("功能说明");
        }
        if (!markdownContent.contains("## 三、技术架构") && !markdownContent.contains("## 技术架构")) {
            missingSections.add("技术架构");
        }
        if (!markdownContent.contains("## 四、技术创新点") && !markdownContent.contains("## 技术创新点")) {
            missingSections.add("技术创新点");
        }
        if (!markdownContent.contains("## 五、应用价值") && !markdownContent.contains("## 应用价值")) {
            missingSections.add("应用价值");
        }

        return missingSections;
    }

    /**
     * 构建ReactAgent实例
     */
    @SuppressWarnings("unused")
    private ReactAgent buildReactAgent(AgentContext context) {
        log.info("[ReactDocWriterAgent] 开始构建ReactAgent");

        ReactAgent agent = (ReactAgent) ReactAgent.builder()
                .name("ReactDocWriterAgent")
                .description("申报说明文档撰写Agent,生成3000-5000字的专业文档")
                .instruction(AGENT_INSTRUCTION)
                .model(chatModel)
                .build();

        log.info("[ReactDocWriterAgent] ReactAgent构建完成");
        return agent;
    }

    @Override
    public String getAgentName() {
        return "ReactDocWriterAgent";
    }

    @Override
    public AgentType getAgentType() {
        return AgentType.REACT_AGENT;
    }
}
