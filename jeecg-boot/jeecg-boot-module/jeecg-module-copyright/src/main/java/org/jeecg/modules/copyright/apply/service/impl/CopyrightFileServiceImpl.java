package org.jeecg.modules.copyright.apply.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.apply.entity.CopyrightFile;
import org.jeecg.modules.copyright.apply.mapper.CopyrightFileMapper;
import org.jeecg.modules.copyright.apply.service.ICopyrightFileService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Date;
import java.util.List;

/**
 * 软著文件记录Service实现
 *
 * @author jeecg-boot
 * @author Claude Code (T007扩展)
 * @since 2025-12-02
 * @version V1.1
 */
@Service
@Slf4j
public class CopyrightFileServiceImpl extends ServiceImpl<CopyrightFileMapper, CopyrightFile>
        implements ICopyrightFileService {

    @Override
    @Transactional(rollbackFor = Exception.class)
    public String saveFileRecord(String sessionId, String fileType, String filename,
                                String filePath, Long fileSize) {
        log.info("[CopyrightFileService] 保存文件记录, sessionId: {}, fileType: {}, filename: {}",
                sessionId, fileType, filename);

        CopyrightFile file = new CopyrightFile();
        file.setSessionId(sessionId);
        file.setFileType(fileType);
        file.setFilename(filename);
        file.setFilePath(filePath);
        file.setFileSize(BigDecimal.valueOf(fileSize));
        file.setCreateTime(new Date());

        // 设置文件分类（根据文件类型）
        file.setFileCategory(mapFileTypeToCategory(fileType));

        // 设置文件扩展名
        String extension = getFileExtension(filename);
        file.setFileExtension(extension);

        // 设置MIME类型
        file.setMimeType(getMimeType(extension));

        // 默认质量状态为待检查
        file.setQualityStatus("pending");

        boolean success = this.save(file);

        if (success) {
            log.info("[CopyrightFileService] 文件记录保存成功, fileId: {}", file.getId());
            return file.getId();
        } else {
            log.error("[CopyrightFileService] 文件记录保存失败");
            throw new RuntimeException("文件记录保存失败");
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateQualityStatus(String fileId, String qualityStatus,
                                      Integer qualityScore, String qualityReportJson) {
        log.info("[CopyrightFileService] 更新文件质量状态, fileId: {}, status: {}, score: {}",
                fileId, qualityStatus, qualityScore);

        CopyrightFile file = this.getById(fileId);
        if (file == null) {
            log.warn("[CopyrightFileService] 文件不存在, fileId: {}", fileId);
            return false;
        }

        file.setQualityStatus(qualityStatus);
        file.setQualityScore(qualityScore);
        file.setQualityReportJson(qualityReportJson);
        file.setUpdateTime(new Date());

        return this.updateById(file);
    }

    @Override
    public List<CopyrightFile> getSessionFiles(String sessionId) {
        log.debug("[CopyrightFileService] 查询会话文件列表, sessionId: {}", sessionId);

        LambdaQueryWrapper<CopyrightFile> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(CopyrightFile::getSessionId, sessionId)
                .orderByDesc(CopyrightFile::getCreateTime);

        return this.list(wrapper);
    }

    @Override
    public List<CopyrightFile> getSessionFilesByType(String sessionId, String fileType) {
        log.debug("[CopyrightFileService] 查询会话特定类型文件, sessionId: {}, fileType: {}",
                sessionId, fileType);

        LambdaQueryWrapper<CopyrightFile> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(CopyrightFile::getSessionId, sessionId)
                .eq(CopyrightFile::getFileType, fileType)
                .orderByDesc(CopyrightFile::getCreateTime);

        return this.list(wrapper);
    }

    @Override
    public CopyrightFile getLatestFileByType(String sessionId, String fileType) {
        log.debug("[CopyrightFileService] 获取最新文件, sessionId: {}, fileType: {}",
                sessionId, fileType);

        LambdaQueryWrapper<CopyrightFile> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(CopyrightFile::getSessionId, sessionId)
                .eq(CopyrightFile::getFileType, fileType)
                .orderByDesc(CopyrightFile::getCreateTime)
                .last("LIMIT 1");

        return this.getOne(wrapper);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public int deleteSessionFiles(String sessionId) {
        log.info("[CopyrightFileService] 删除会话所有文件, sessionId: {}", sessionId);

        LambdaQueryWrapper<CopyrightFile> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(CopyrightFile::getSessionId, sessionId);

        List<CopyrightFile> files = this.list(wrapper);
        int count = files.size();

        if (count > 0) {
            this.remove(wrapper);
            log.info("[CopyrightFileService] 删除文件数量: {}", count);
        }

        return count;
    }

    @Override
    public boolean fileExists(String fileId) {
        return this.getById(fileId) != null;
    }

    @Override
    public CopyrightFile getByFilePath(String filePath) {
        LambdaQueryWrapper<CopyrightFile> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(CopyrightFile::getFilePath, filePath)
                .orderByDesc(CopyrightFile::getCreateTime)
                .last("LIMIT 1");

        return this.getOne(wrapper);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateFileMetadata(String fileId, Integer codeLines, Integer docWordCount) {
        log.info("[CopyrightFileService] 更新文件元数据, fileId: {}, codeLines: {}, docWordCount: {}",
                fileId, codeLines, docWordCount);

        CopyrightFile file = this.getById(fileId);
        if (file == null) {
            log.warn("[CopyrightFileService] 文件不存在, fileId: {}", fileId);
            return false;
        }

        file.setCodeLines(codeLines);
        file.setDocWordCount(docWordCount);
        file.setUpdateTime(new Date());

        return this.updateById(file);
    }

    // ==================== 私有辅助方法 ====================

    /**
     * 根据文件类型映射到文件分类
     */
    private String mapFileTypeToCategory(String fileType) {
        return switch (fileType) {
            case "source_code" -> "代码文件";
            case "info_form" -> "申报表格";
            case "desc_doc" -> "说明文档";
            default -> "其他";
        };
    }

    /**
     * 获取文件扩展名
     */
    private String getFileExtension(String filename) {
        if (filename == null || !filename.contains(".")) {
            return "";
        }
        return filename.substring(filename.lastIndexOf(".") + 1).toLowerCase();
    }

    /**
     * 根据扩展名获取MIME类型
     */
    private String getMimeType(String extension) {
        return switch (extension) {
            case "zip" -> "application/zip";
            case "docx" -> "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
            case "doc" -> "application/msword";
            case "pdf" -> "application/pdf";
            case "txt" -> "text/plain";
            case "java" -> "text/x-java-source";
            case "py" -> "text/x-python";
            case "js" -> "text/javascript";
            case "html" -> "text/html";
            case "xml" -> "application/xml";
            case "json" -> "application/json";
            default -> "application/octet-stream";
        };
    }
}

