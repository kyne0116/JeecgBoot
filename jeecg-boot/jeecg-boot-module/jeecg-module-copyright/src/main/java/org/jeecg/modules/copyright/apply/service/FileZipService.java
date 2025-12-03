package org.jeecg.modules.copyright.apply.service;

import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.apply.entity.CopyrightFile;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
 * 文件ZIP打包服务
 *
 * 提供批量文件打包下载功能
 *
 * @author Claude Code
 * @since 2025-12-03 (T007)
 */
@Service
@Slf4j
public class FileZipService {

    @Value("${jeecg.path.upload:/opt/upFiles}")
    private String uploadPath;

    /**
     * 打包会话所有文件为ZIP
     *
     * @param sessionId 会话ID
     * @param files 文件列表
     * @return ZIP文件路径
     * @throws IOException IO异常
     */
    public String packSessionFiles(String sessionId, List<CopyrightFile> files) throws IOException {
        log.info("[FileZipService] 开始打包会话文件, sessionId: {}, fileCount: {}",
                sessionId, files.size());

        // 创建临时ZIP文件
        String zipFilename = "copyright_" + sessionId + "_" + System.currentTimeMillis() + ".zip";
        Path zipPath = Paths.get(uploadPath, "temp", zipFilename);

        // 确保临时目录存在
        Files.createDirectories(zipPath.getParent());

        try (FileOutputStream fos = new FileOutputStream(zipPath.toFile());
             ZipOutputStream zos = new ZipOutputStream(fos)) {

            // 添加每个文件到ZIP
            for (CopyrightFile file : files) {
                addFileToZip(zos, file);
            }

            log.info("[FileZipService] ZIP打包完成, zipPath: {}", zipPath);
            return zipPath.toString();

        } catch (IOException e) {
            log.error("[FileZipService] ZIP打包失败", e);
            // 清理失败的ZIP文件
            try {
                Files.deleteIfExists(zipPath);
            } catch (IOException ex) {
                log.warn("[FileZipService] 清理失败的ZIP文件异常", ex);
            }
            throw e;
        }
    }

    /**
     * 添加文件到ZIP流
     *
     * @param zos ZipOutputStream
     * @param fileRecord 文件记录
     * @throws IOException IO异常
     */
    private void addFileToZip(ZipOutputStream zos, CopyrightFile fileRecord) throws IOException {
        File file = new File(fileRecord.getFilePath());

        // 检查文件是否存在
        if (!file.exists()) {
            log.warn("[FileZipService] 文件不存在，跳过: {}", fileRecord.getFilename());
            return;
        }

        // 根据文件类型创建目录结构
        String entryPath = buildEntryPath(fileRecord);

        log.debug("[FileZipService] 添加文件到ZIP: {}", entryPath);

        // 创建ZIP条目
        ZipEntry zipEntry = new ZipEntry(entryPath);
        zipEntry.setTime(file.lastModified());
        zos.putNextEntry(zipEntry);

        // 写入文件内容
        try (FileInputStream fis = new FileInputStream(file)) {
            byte[] buffer = new byte[8192];
            int length;
            while ((length = fis.read(buffer)) > 0) {
                zos.write(buffer, 0, length);
            }
        }

        zos.closeEntry();
    }

    /**
     * 构建ZIP条目路径（带目录结构）
     *
     * @param fileRecord 文件记录
     * @return ZIP条目路径
     */
    private String buildEntryPath(CopyrightFile fileRecord) {
        String directory = switch (fileRecord.getFileType()) {
            case "source_code" -> "1-源代码/";
            case "info_form" -> "2-申报表格/";
            case "desc_doc" -> "3-说明文档/";
            default -> "其他/";
        };

        return directory + fileRecord.getFilename();
    }

    /**
     * 清理临时ZIP文件
     *
     * @param zipFilePath ZIP文件路径
     * @return 是否成功
     */
    public boolean cleanupTempZip(String zipFilePath) {
        try {
            Path path = Paths.get(zipFilePath);
            if (Files.exists(path)) {
                Files.delete(path);
                log.info("[FileZipService] 清理临时ZIP文件成功: {}", zipFilePath);
                return true;
            }
        } catch (IOException e) {
            log.warn("[FileZipService] 清理临时ZIP文件失败: {}", zipFilePath, e);
        }
        return false;
    }

    /**
     * 获取ZIP文件大小
     *
     * @param zipFilePath ZIP文件路径
     * @return 文件大小（字节）
     */
    public long getZipFileSize(String zipFilePath) {
        try {
            Path path = Paths.get(zipFilePath);
            if (Files.exists(path)) {
                return Files.size(path);
            }
        } catch (IOException e) {
            log.warn("[FileZipService] 获取ZIP文件大小失败: {}", zipFilePath, e);
        }
        return 0;
    }

    /**
     * 计算打包后预估大小
     *
     * @param files 文件列表
     * @return 预估大小（字节）
     */
    public long estimateZipSize(List<CopyrightFile> files) {
        long totalSize = 0;
        for (CopyrightFile file : files) {
            totalSize += file.getFileSize().longValue();
        }
        // ZIP压缩通常可以减少20-30%，这里保守估计为原始大小的80%
        return (long) (totalSize * 0.8);
    }
}
