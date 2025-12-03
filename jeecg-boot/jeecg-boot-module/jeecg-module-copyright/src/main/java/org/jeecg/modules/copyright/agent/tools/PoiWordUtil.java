package org.jeecg.modules.copyright.agent.tools;

import lombok.extern.slf4j.Slf4j;
import org.apache.poi.xwpf.usermodel.*;
import org.jeecg.modules.copyright.vo.CopyrightRequirement;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;

/**
 * Apache POI Word文档工具类
 * <p>
 * 用于填充软著信息采集表模板
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Component
@Slf4j
public class PoiWordUtil {

    @Value("${jeecg.path.upload:/opt/upFiles}")
    private String uploadPath;

    private static final String WORD_TEMPLATE_SUBDIR = "copyright/templates";
    private static final String WORD_OUTPUT_SUBDIR = "copyright/info_forms";
    private static final String TEMPLATE_FILENAME = "软著信息采集表模板.docx";

    /**
     * 填充软著信息采集表
     *
     * @param requirement 软著申报需求
     * @param sessionId   会话ID
     * @return 生成的Word文档路径
     */
    public String fillCopyrightInfoForm(CopyrightRequirement requirement, String sessionId) throws IOException {
        log.info("[PoiWordUtil] 开始填充软著信息采集表, sessionId: {}", sessionId);

        // 加载模板文件
        Path templatePath = getTemplatePath();
        if (!Files.exists(templatePath)) {
            throw new IOException("模板文件不存在: " + templatePath);
        }

        try (FileInputStream fis = new FileInputStream(templatePath.toFile());
             XWPFDocument document = new XWPFDocument(fis)) {

            // 准备填充数据
            Map<String, String> fillData = prepareFillData(requirement);

            // 替换文档中的占位符
            replacePlaceholders(document, fillData);

            // 填充功能列表动态表格
            fillFeatureTable(document, requirement.getFeatures());

            // 保存填充后的文档
            String outputFilePath = saveDocument(document, sessionId);

            log.info("[PoiWordUtil] 软著信息采集表填充完成: {}", outputFilePath);
            return outputFilePath;
        }
    }

    /**
     * 准备填充数据
     */
    private Map<String, String> prepareFillData(CopyrightRequirement requirement) {
        String applicantName = requirement.getApplicant() != null ? requirement.getApplicant().getName() : "";
        String applicantType = requirement.getApplicant() != null ? requirement.getApplicant().getType() : "individual";

        return Map.ofEntries(
                Map.entry("{{SOFTWARE_NAME}}", requirement.getSoftwareName()),
                Map.entry("{{SHORT_NAME}}", requirement.getShortName()),
                Map.entry("{{VERSION}}", requirement.getVersion()),
                Map.entry("{{CATEGORY}}", requirement.getCategory()),
                Map.entry("{{CODE_LANGUAGE}}", requirement.getCodeLanguage()),
                Map.entry("{{TECH_STACK}}", requirement.getTechStack()),
                Map.entry("{{APPLICANT_NAME}}", applicantName),
                Map.entry("{{APPLICANT_TYPE}}", "enterprise".equals(applicantType) ? "企业" : "个人"),
                Map.entry("{{CONTACT_PERSON}}", applicantName),
                Map.entry("{{CONTACT_PHONE}}", ""),
                Map.entry("{{FILL_DATE}}", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy年MM月dd日")))
        );
    }

    /**
     * 替换文档中的占位符
     */
    private void replacePlaceholders(XWPFDocument document, Map<String, String> fillData) {
        // 替换段落中的占位符
        for (XWPFParagraph paragraph : document.getParagraphs()) {
            replaceInParagraph(paragraph, fillData);
        }

        // 替换表格中的占位符
        for (XWPFTable table : document.getTables()) {
            for (XWPFTableRow row : table.getRows()) {
                for (XWPFTableCell cell : row.getTableCells()) {
                    for (XWPFParagraph paragraph : cell.getParagraphs()) {
                        replaceInParagraph(paragraph, fillData);
                    }
                }
            }
        }
    }

    /**
     * 在段落中替换占位符
     */
    private void replaceInParagraph(XWPFParagraph paragraph, Map<String, String> fillData) {
        for (XWPFRun run : paragraph.getRuns()) {
            String text = run.getText(0);
            if (text != null) {
                for (Map.Entry<String, String> entry : fillData.entrySet()) {
                    if (text.contains(entry.getKey())) {
                        text = text.replace(entry.getKey(), entry.getValue());
                    }
                }
                run.setText(text, 0);
            }
        }
    }

    /**
     * 填充功能列表表格
     */
    private void fillFeatureTable(XWPFDocument document, List<CopyrightRequirement.SoftwareFeature> features) {
        if (features == null || features.isEmpty()) {
            return;
        }

        // 查找功能列表表格(假设是第2个表格)
        List<XWPFTable> tables = document.getTables();
        if (tables.size() < 2) {
            log.warn("[PoiWordUtil] 文档中表格数量不足,无法填充功能列表");
            return;
        }

        XWPFTable featureTable = tables.get(1); // 假设功能列表是第2个表格

        // 获取表头行(第一行)
        XWPFTableRow headerRow = featureTable.getRow(0);

        // 从第2行开始填充功能(第1行是表头)
        for (int i = 0; i < features.size(); i++) {
            XWPFTableRow row;
            if (i + 1 < featureTable.getRows().size()) {
                // 使用现有行
                row = featureTable.getRow(i + 1);
            } else {
                // 添加新行
                row = featureTable.createRow();
            }

            // 填充序号和功能名称
            row.getCell(0).setText(String.valueOf(i + 1));
            row.getCell(1).setText(features.get(i).getName());
        }

        log.info("[PoiWordUtil] 功能列表填充完成, 共{}项功能", features.size());
    }

    /**
     * 保存文档
     */
    private String saveDocument(XWPFDocument document, String sessionId) throws IOException {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        String filename = String.format("软著信息采集表_%s_%s.docx", sessionId, timestamp);

        Path outputDir = Paths.get(uploadPath, WORD_OUTPUT_SUBDIR);
        Files.createDirectories(outputDir);

        Path outputPath = outputDir.resolve(filename);

        try (FileOutputStream fos = new FileOutputStream(outputPath.toFile())) {
            document.write(fos);
        }

        return outputPath.toString();
    }

    /**
     * 获取模板文件路径
     */
    private Path getTemplatePath() {
        return Paths.get(uploadPath, WORD_TEMPLATE_SUBDIR, TEMPLATE_FILENAME);
    }

    /**
     * 验证模板文件是否存在
     */
    public boolean validateTemplate() {
        Path templatePath = getTemplatePath();
        boolean exists = Files.exists(templatePath);

        if (!exists) {
            log.warn("[PoiWordUtil] 模板文件不存在: {}", templatePath);
        } else {
            log.info("[PoiWordUtil] 模板文件存在: {}", templatePath);
        }

        return exists;
    }
}
