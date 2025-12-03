package org.jeecg.modules.copyright.agent.tools;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

/**
 * 源代码ZIP打包工具
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Component
@Slf4j
public class CodeZipPackager {

    @Value("${jeecg.path.upload:/opt/upFiles}")
    private String uploadPath;

    private static final String CODE_ZIP_SUBDIR = "copyright/source_code";

    /**
     * 将源代码文件打包为ZIP
     *
     * @param sourceFiles 源代码文件映射(路径 -> 内容)
     * @param sessionId   会话ID
     * @return ZIP文件的绝对路径
     */
    public String packageSourceCode(Map<String, String> sourceFiles, String sessionId) throws IOException {
        log.info("[CodeZipPackager] 开始打包源代码, 文件数量: {}, sessionId: {}",
                sourceFiles.size(), sessionId);

        // 创建ZIP文件路径
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
        String zipFileName = String.format("source_code_%s_%s.zip", sessionId, timestamp);

        Path zipDirPath = Paths.get(uploadPath, CODE_ZIP_SUBDIR);
        Files.createDirectories(zipDirPath);

        Path zipFilePath = zipDirPath.resolve(zipFileName);

        // 创建ZIP文件
        try (ZipOutputStream zos = new ZipOutputStream(
                new FileOutputStream(zipFilePath.toFile()), StandardCharsets.UTF_8)) {

            for (Map.Entry<String, String> entry : sourceFiles.entrySet()) {
                String relativePath = entry.getKey();
                String content = entry.getValue();

                // 创建ZIP条目
                ZipEntry zipEntry = new ZipEntry(relativePath);
                zos.putNextEntry(zipEntry);

                // 写入文件内容
                byte[] bytes = content.getBytes(StandardCharsets.UTF_8);
                zos.write(bytes, 0, bytes.length);
                zos.closeEntry();

                log.debug("[CodeZipPackager] 添加文件到ZIP: {}", relativePath);
            }

            log.info("[CodeZipPackager] ZIP打包完成: {}", zipFilePath);
        }

        return zipFilePath.toString();
    }

    /**
     * 删除旧的ZIP文件(清理临时文件)
     */
    public void cleanupOldZipFiles(int daysToKeep) {
        try {
            Path zipDirPath = Paths.get(uploadPath, CODE_ZIP_SUBDIR);
            if (!Files.exists(zipDirPath)) {
                return;
            }

            long cutoffTime = System.currentTimeMillis() - (daysToKeep * 24L * 60 * 60 * 1000);

            Files.list(zipDirPath)
                    .filter(path -> path.toString().endsWith(".zip"))
                    .filter(path -> {
                        try {
                            return Files.getLastModifiedTime(path).toMillis() < cutoffTime;
                        } catch (IOException e) {
                            return false;
                        }
                    })
                    .forEach(path -> {
                        try {
                            Files.delete(path);
                            log.info("[CodeZipPackager] 删除过期ZIP文件: {}", path);
                        } catch (IOException e) {
                            log.warn("[CodeZipPackager] 删除文件失败: {}", path, e);
                        }
                    });

        } catch (IOException e) {
            log.error("[CodeZipPackager] 清理ZIP文件失败", e);
        }
    }
}
