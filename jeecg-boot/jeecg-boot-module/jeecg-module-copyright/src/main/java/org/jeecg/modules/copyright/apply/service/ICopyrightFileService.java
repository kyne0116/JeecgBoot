package org.jeecg.modules.copyright.apply.service;

import org.jeecg.modules.copyright.apply.entity.CopyrightFile;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;

/**
 * 软著文件记录Service
 *
 * @author jeecg-boot
 * @author Claude Code (T007扩展)
 * @since 2025-12-02
 * @version V1.1
 */
public interface ICopyrightFileService extends IService<CopyrightFile> {

    /**
     * 保存文件记录
     *
     * @param sessionId 会话ID
     * @param fileType 文件类型（source_code/info_form/desc_doc）
     * @param filename 文件名
     * @param filePath 文件路径
     * @param fileSize 文件大小（字节）
     * @return 文件记录ID
     */
    String saveFileRecord(String sessionId, String fileType, String filename,
                         String filePath, Long fileSize);

    /**
     * 更新文件质量状态
     *
     * @param fileId 文件ID
     * @param qualityStatus 质量状态（checking/passed/failed）
     * @param qualityScore 质量得分（0-100）
     * @param qualityReportJson 质检报告JSON
     * @return 是否成功
     */
    boolean updateQualityStatus(String fileId, String qualityStatus,
                               Integer qualityScore, String qualityReportJson);

    /**
     * 查询会话的文件列表
     *
     * @param sessionId 会话ID
     * @return 文件列表（按创建时间倒序）
     */
    List<CopyrightFile> getSessionFiles(String sessionId);

    /**
     * 查询会话的特定类型文件列表
     *
     * @param sessionId 会话ID
     * @param fileType 文件类型
     * @return 文件列表
     */
    List<CopyrightFile> getSessionFilesByType(String sessionId, String fileType);

    /**
     * 获取最新版本文件
     *
     * @param sessionId 会话ID
     * @param fileType 文件类型
     * @return 最新版本的文件（按创建时间倒序取第一个）
     */
    CopyrightFile getLatestFileByType(String sessionId, String fileType);

    /**
     * 删除会话所有文件记录
     *
     * @param sessionId 会话ID
     * @return 删除数量
     */
    int deleteSessionFiles(String sessionId);

    /**
     * 检查文件是否存在
     *
     * @param fileId 文件ID
     * @return 是否存在
     */
    boolean fileExists(String fileId);

    /**
     * 根据文件路径获取文件记录
     *
     * @param filePath 文件路径
     * @return 文件记录
     */
    CopyrightFile getByFilePath(String filePath);

    /**
     * 更新文件元数据（代码行数、文档字数等）
     *
     * @param fileId 文件ID
     * @param codeLines 代码行数
     * @param docWordCount 文档字数
     * @return 是否成功
     */
    boolean updateFileMetadata(String fileId, Integer codeLines, Integer docWordCount);
}
