package org.jeecg.modules.copyright.agent.tools;

import lombok.extern.slf4j.Slf4j;
import org.apache.poi.xwpf.usermodel.*;
import org.jeecg.modules.copyright.vo.CopyrightRequirement;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

/**
 * Markdown转Word工具类
 * <p>
 * 将Markdown格式的申报说明文档转换为Word文档,并设置仿宋字体
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Component
@Slf4j
public class MarkdownToWordConverter {

    @Value("${jeecg.path.upload:/opt/upFiles}")
    private String uploadPath;

    private static final String DOC_OUTPUT_SUBDIR = "copyright/desc_docs";
    private static final String FONT_NAME = "仿宋";
    private static final int FONT_SIZE = 24; // POI中字号 = 实际字号 * 2

    /**
     * 将Markdown内容转换为Word文档
     *
     * @param markdownContent Markdown内容
     * @param sessionId       会话ID
     * @return Word文档路径
     */
    public String convertMarkdownToWord(String markdownContent, String sessionId) throws IOException {
        log.info("[MarkdownToWordConverter] 开始转换Markdown到Word, sessionId: {}", sessionId);

        // 创建Word文档
        XWPFDocument document = new XWPFDocument();

        // 解析Markdown并转换为Word
        parseMarkdownToWord(document, markdownContent);

        // 保存文档
        String filePath = saveDocument(document, sessionId);

        log.info("[MarkdownToWordConverter] Markdown转Word完成: {}", filePath);
        return filePath;
    }

    /**
     * 解析Markdown并转换为Word段落
     */
    private void parseMarkdownToWord(XWPFDocument document, String markdownContent) {
        String[] lines = markdownContent.split("\n");

        for (String line : lines) {
            line = line.trim();

            if (line.isEmpty()) {
                // 空行跳过
                continue;
            }

            if (line.startsWith("# ")) {
                // 一级标题
                createHeading(document, line.substring(2), 1);
            } else if (line.startsWith("## ")) {
                // 二级标题
                createHeading(document, line.substring(3), 2);
            } else if (line.startsWith("### ")) {
                // 三级标题
                createHeading(document, line.substring(4), 3);
            } else if (line.startsWith("- ") || line.startsWith("* ")) {
                // 列表项
                createListItem(document, line.substring(2));
            } else if (line.matches("^\\d+\\.\\s.*")) {
                // 有序列表
                createOrderedListItem(document, line);
            } else {
                // 普通段落
                createParagraph(document, line);
            }
        }
    }

    /**
     * 创建标题段落
     */
    private void createHeading(XWPFDocument document, String text, int level) {
        XWPFParagraph paragraph = document.createParagraph();
        XWPFRun run = paragraph.createRun();

        run.setText(text);
        run.setFontFamily(FONT_NAME);
        run.setBold(true);

        // 根据标题级别设置字号
        int fontSize = switch (level) {
            case 1 -> 32; // 16号字
            case 2 -> 28; // 14号字
            case 3 -> 26; // 13号字
            default -> FONT_SIZE;
        };

        run.setFontSize(fontSize / 2);
    }

    /**
     * 创建无序列表项
     */
    private void createListItem(XWPFDocument document, String text) {
        XWPFParagraph paragraph = document.createParagraph();
        paragraph.setIndentationLeft(400); // 设置缩进

        XWPFRun run = paragraph.createRun();
        run.setText("• " + text);
        run.setFontFamily(FONT_NAME);
        run.setFontSize(FONT_SIZE / 2);
    }

    /**
     * 创建有序列表项
     */
    private void createOrderedListItem(XWPFDocument document, String text) {
        XWPFParagraph paragraph = document.createParagraph();
        paragraph.setIndentationLeft(400); // 设置缩进

        XWPFRun run = paragraph.createRun();
        run.setText(text);
        run.setFontFamily(FONT_NAME);
        run.setFontSize(FONT_SIZE / 2);
    }

    /**
     * 创建普通段落
     */
    private void createParagraph(XWPFDocument document, String text) {
        XWPFParagraph paragraph = document.createParagraph();

        // 设置段落首行缩进(两个字符)
        paragraph.setIndentationFirstLine(480);

        XWPFRun run = paragraph.createRun();
        run.setText(text);
        run.setFontFamily(FONT_NAME);
        run.setFontSize(FONT_SIZE / 2); // 12号字
    }

    /**
     * 保存Word文档
     */
    private String saveDocument(XWPFDocument document, String sessionId) throws IOException {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        String filename = String.format("申报说明文档_%s_%s.docx", sessionId, timestamp);

        Path outputDir = Paths.get(uploadPath, DOC_OUTPUT_SUBDIR);
        Files.createDirectories(outputDir);

        Path outputPath = outputDir.resolve(filename);

        try (FileOutputStream fos = new FileOutputStream(outputPath.toFile())) {
            document.write(fos);
        }

        // 关闭文档
        document.close();

        return outputPath.toString();
    }

    /**
     * 统计中文字数(不含标点和空格)
     */
    public int countChineseCharacters(String content) {
        if (content == null || content.isEmpty()) {
            return 0;
        }

        int count = 0;
        for (char c : content.toCharArray()) {
            // 统计中文字符和英文字母、数字
            if (Character.isLetterOrDigit(c) || isChinese(c)) {
                count++;
            }
        }

        return count;
    }

    /**
     * 判断是否为中文字符
     */
    private boolean isChinese(char c) {
        Character.UnicodeBlock ub = Character.UnicodeBlock.of(c);
        return ub == Character.UnicodeBlock.CJK_UNIFIED_IDEOGRAPHS
                || ub == Character.UnicodeBlock.CJK_COMPATIBILITY_IDEOGRAPHS
                || ub == Character.UnicodeBlock.CJK_UNIFIED_IDEOGRAPHS_EXTENSION_A
                || ub == Character.UnicodeBlock.GENERAL_PUNCTUATION
                || ub == Character.UnicodeBlock.CJK_SYMBOLS_AND_PUNCTUATION
                || ub == Character.UnicodeBlock.HALFWIDTH_AND_FULLWIDTH_FORMS;
    }
}
