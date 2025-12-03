package org.jeecg.modules.copyright.apply.service;

import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.apply.entity.CopyrightFile;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import java.io.File;
import java.math.BigDecimal;
import java.util.Date;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * T007 - 文件管理功能测试
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@SpringBootTest
@ActiveProfiles("test")
@Slf4j
public class CopyrightFileServiceTest {

    @Autowired
    private ICopyrightFileService fileService;

    @Autowired
    private FileZipService zipService;

    /**
     * 测试1：保存文件记录
     */
    @Test
    @DisplayName("测试保存文件记录")
    @Transactional
    public void testSaveFileRecord() {
        log.info("========== 测试保存文件记录 ==========");

        String sessionId = "test_session_" + System.currentTimeMillis();
        String filename = "test_source_code.zip";
        String filePath = "/tmp/test/" + filename;
        Long fileSize = 1024000L; // 1MB

        String fileId = fileService.saveFileRecord(
                sessionId,
                "source_code",
                filename,
                filePath,
                fileSize
        );

        assertNotNull(fileId, "文件ID不应该为null");
        log.info("✅ 文件记录保存成功, fileId: {}", fileId);

        // 验证保存的记录
        CopyrightFile file = fileService.getById(fileId);
        assertNotNull(file, "文件记录应该存在");
        assertEquals(sessionId, file.getSessionId());
        assertEquals(filename, file.getFilename());
        assertEquals("source_code", file.getFileType());
        assertEquals("代码文件", file.getFileCategory());
        assertEquals("zip", file.getFileExtension());
        assertEquals("application/zip", file.getMimeType());

        log.info("========== 测试保存文件记录完成 ==========");
    }

    /**
     * 测试2：更新文件质量状态
     */
    @Test
    @DisplayName("测试更新文件质量状态")
    @Transactional
    public void testUpdateQualityStatus() {
        log.info("========== 测试更新文件质量状态 ==========");

        // 1. 先创建文件记录
        String sessionId = "test_session_" + System.currentTimeMillis();
        String fileId = fileService.saveFileRecord(
                sessionId,
                "desc_doc",
                "test_doc.docx",
                "/tmp/test/test_doc.docx",
                50000L
        );

        // 2. 更新质量状态
        boolean success = fileService.updateQualityStatus(
                fileId,
                "passed",
                95,
                "{\"score\":95,\"status\":\"passed\"}"
        );

        assertTrue(success, "质量状态更新应该成功");

        // 3. 验证更新
        CopyrightFile file = fileService.getById(fileId);
        assertEquals("passed", file.getQualityStatus());
        assertEquals(95, file.getQualityScore());
        assertNotNull(file.getQualityReportJson());

        log.info("✅ 质量状态更新成功");
        log.info("========== 测试更新文件质量状态完成 ==========");
    }

    /**
     * 测试3：查询会话文件列表
     */
    @Test
    @DisplayName("测试查询会话文件列表")
    @Transactional
    public void testGetSessionFiles() {
        log.info("========== 测试查询会话文件列表 ==========");

        String sessionId = "test_session_" + System.currentTimeMillis();

        // 1. 创建多个文件记录
        fileService.saveFileRecord(sessionId, "source_code", "code.zip", "/tmp/code.zip", 1000L);
        fileService.saveFileRecord(sessionId, "info_form", "form.docx", "/tmp/form.docx", 500L);
        fileService.saveFileRecord(sessionId, "desc_doc", "doc.docx", "/tmp/doc.docx", 800L);

        // 2. 查询文件列表
        List<CopyrightFile> files = fileService.getSessionFiles(sessionId);

        assertNotNull(files, "文件列表不应该为null");
        assertEquals(3, files.size(), "应该有3个文件");

        log.info("✅ 查询到文件数量: {}", files.size());
        for (CopyrightFile file : files) {
            log.info("  - 文件: {}, 类型: {}, 大小: {} bytes",
                    file.getFilename(), file.getFileType(), file.getFileSize());
        }

        log.info("========== 测试查询会话文件列表完成 ==========");
    }

    /**
     * 测试4：按类型查询文件
     */
    @Test
    @DisplayName("测试按类型查询文件")
    @Transactional
    public void testGetSessionFilesByType() {
        log.info("========== 测试按类型查询文件 ==========");

        String sessionId = "test_session_" + System.currentTimeMillis();

        // 1. 创建不同类型的文件
        fileService.saveFileRecord(sessionId, "source_code", "code1.zip", "/tmp/code1.zip", 1000L);
        fileService.saveFileRecord(sessionId, "source_code", "code2.zip", "/tmp/code2.zip", 1000L);
        fileService.saveFileRecord(sessionId, "info_form", "form.docx", "/tmp/form.docx", 500L);

        // 2. 查询source_code类型的文件
        List<CopyrightFile> codeFiles = fileService.getSessionFilesByType(sessionId, "source_code");

        assertNotNull(codeFiles, "文件列表不应该为null");
        assertEquals(2, codeFiles.size(), "应该有2个源代码文件");

        for (CopyrightFile file : codeFiles) {
            assertEquals("source_code", file.getFileType());
        }

        log.info("✅ 查询到源代码文件数量: {}", codeFiles.size());

        log.info("========== 测试按类型查询文件完成 ==========");
    }

    /**
     * 测试5：获取最新版本文件
     */
    @Test
    @DisplayName("测试获取最新版本文件")
    @Transactional
    public void testGetLatestFileByType() throws InterruptedException {
        log.info("========== 测试获取最新版本文件 ==========");

        String sessionId = "test_session_" + System.currentTimeMillis();

        // 1. 创建多个相同类型的文件（模拟版本）
        fileService.saveFileRecord(sessionId, "desc_doc", "doc_v1.docx", "/tmp/doc_v1.docx", 500L);
        Thread.sleep(100); // 确保时间戳不同
        fileService.saveFileRecord(sessionId, "desc_doc", "doc_v2.docx", "/tmp/doc_v2.docx", 600L);
        Thread.sleep(100);
        String latestId = fileService.saveFileRecord(sessionId, "desc_doc", "doc_v3.docx", "/tmp/doc_v3.docx", 700L);

        // 2. 获取最新版本
        CopyrightFile latestFile = fileService.getLatestFileByType(sessionId, "desc_doc");

        assertNotNull(latestFile, "最新文件不应该为null");
        assertEquals(latestId, latestFile.getId(), "应该返回最新创建的文件");
        assertEquals("doc_v3.docx", latestFile.getFilename());

        log.info("✅ 获取最新文件成功: {}", latestFile.getFilename());

        log.info("========== 测试获取最新版本文件完成 ==========");
    }

    /**
     * 测试6：删除会话所有文件
     */
    @Test
    @DisplayName("测试删除会话所有文件")
    @Transactional
    public void testDeleteSessionFiles() {
        log.info("========== 测试删除会话所有文件 ==========");

        String sessionId = "test_session_" + System.currentTimeMillis();

        // 1. 创建文件记录
        fileService.saveFileRecord(sessionId, "source_code", "code.zip", "/tmp/code.zip", 1000L);
        fileService.saveFileRecord(sessionId, "info_form", "form.docx", "/tmp/form.docx", 500L);

        // 2. 验证文件已创建
        List<CopyrightFile> filesBefore = fileService.getSessionFiles(sessionId);
        assertEquals(2, filesBefore.size());

        // 3. 删除会话所有文件
        int count = fileService.deleteSessionFiles(sessionId);
        assertEquals(2, count, "应该删除2个文件");

        // 4. 验证文件已删除
        List<CopyrightFile> filesAfter = fileService.getSessionFiles(sessionId);
        assertEquals(0, filesAfter.size(), "所有文件应该已删除");

        log.info("✅ 成功删除 {} 个文件", count);

        log.info("========== 测试删除会话所有文件完成 ==========");
    }

    /**
     * 测试7：更新文件元数据
     */
    @Test
    @DisplayName("测试更新文件元数据")
    @Transactional
    public void testUpdateFileMetadata() {
        log.info("========== 测试更新文件元数据 ==========");

        // 1. 创建文件记录
        String sessionId = "test_session_" + System.currentTimeMillis();
        String fileId = fileService.saveFileRecord(
                sessionId,
                "source_code",
                "code.zip",
                "/tmp/code.zip",
                1000L
        );

        // 2. 更新元数据
        boolean success = fileService.updateFileMetadata(fileId, 5500, null);
        assertTrue(success, "更新元数据应该成功");

        // 3. 验证更新
        CopyrightFile file = fileService.getById(fileId);
        assertEquals(5500, file.getCodeLines());

        log.info("✅ 文件元数据更新成功, codeLines: {}", file.getCodeLines());

        log.info("========== 测试更新文件元数据完成 ==========");
    }

    /**
     * 测试8：ZIP打包预估大小
     */
    @Test
    @DisplayName("测试ZIP打包预估大小")
    public void testEstimateZipSize() {
        log.info("========== 测试ZIP打包预估大小 ==========");

        // 创建测试文件列表
        List<CopyrightFile> files = List.of(
                createTestFile("file1.zip", 1000L),
                createTestFile("file2.docx", 500L),
                createTestFile("file3.docx", 800L)
        );

        long estimatedSize = zipService.estimateZipSize(files);

        assertTrue(estimatedSize > 0, "预估大小应该大于0");
        assertTrue(estimatedSize < 2300, "预估大小应该小于原始大小");

        log.info("✅ 原始大小: {} bytes, 预估ZIP大小: {} bytes", 2300, estimatedSize);

        log.info("========== 测试ZIP打包预估大小完成 ==========");
    }

    // ==================== 辅助方法 ====================

    private CopyrightFile createTestFile(String filename, Long size) {
        CopyrightFile file = new CopyrightFile();
        file.setFilename(filename);
        file.setFileSize(BigDecimal.valueOf(size));
        file.setCreateTime(new Date());
        return file;
    }
}
