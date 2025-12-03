package org.jeecg.modules.copyright.apply.service;

import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.apply.entity.CopyrightFile;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.InputStreamResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

/**
 * 文件下载服务
 *
 * 提供单文件下载功能，支持流式下载
 *
 * @author Claude Code
 * @since 2025-12-03 (T007)
 */
@Service
@Slf4j
public class FileDownloadService {

    @Value("${jeecg.path.upload:/opt/upFiles}")
    private String uploadPath;

    /**
     * 下载单个文件
     *
     * @param fileRecord 文件记录
     * @return ResponseEntity包含文件流
     * @throws FileNotFoundException 文件不存在
     */
    public ResponseEntity<Resource> downloadFile(CopyrightFile fileRecord) throws FileNotFoundException {
        log.info("[FileDownloadService] 开始下载文件, fileId: {}, filename: {}",
                fileRecord.getId(), fileRecord.getFilename());

        // 获取文件路径
        String filePath = fileRecord.getFilePath();
        File file = new File(filePath);

        // 检查文件是否存在
        if (!file.exists()) {
            log.error("[FileDownloadService] 文件不存在, filePath: {}", filePath);
            throw new FileNotFoundException("文件不存在: " + fileRecord.getFilename());
        }

        // 检查文件是否可读
        if (!file.canRead()) {
            log.error("[FileDownloadService] 文件不可读, filePath: {}", filePath);
            throw new RuntimeException("文件不可读: " + fileRecord.getFilename());
        }

        try {
            // 创建文件输入流
            FileInputStream inputStream = new FileInputStream(file);
            InputStreamResource resource = new InputStreamResource(inputStream);

            // 编码文件名（支持中文）
            String encodedFilename = encodeFilename(fileRecord.getFilename());

            // 构建响应头
            HttpHeaders headers = new HttpHeaders();
            headers.add(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + encodedFilename + "\"");
            headers.add(HttpHeaders.CONTENT_TYPE, fileRecord.getMimeType());
            headers.add(HttpHeaders.CONTENT_LENGTH, String.valueOf(file.length()));
            headers.add(HttpHeaders.CACHE_CONTROL, "no-cache, no-store, must-revalidate");
            headers.add(HttpHeaders.PRAGMA, "no-cache");
            headers.add(HttpHeaders.EXPIRES, "0");

            log.info("[FileDownloadService] 文件下载成功, fileId: {}, size: {} bytes",
                    fileRecord.getId(), file.length());

            // 返回文件流响应
            return ResponseEntity.ok()
                    .headers(headers)
                    .contentLength(file.length())
                    .contentType(MediaType.parseMediaType(fileRecord.getMimeType()))
                    .body(resource);

        } catch (FileNotFoundException e) {
            log.error("[FileDownloadService] 文件不存在异常", e);
            throw e;
        } catch (Exception e) {
            log.error("[FileDownloadService] 文件下载失败", e);
            throw new RuntimeException("文件下载失败: " + e.getMessage(), e);
        }
    }

    /**
     * 获取文件大小（字节）
     *
     * @param filePath 文件路径
     * @return 文件大小
     */
    public long getFileSize(String filePath) {
        File file = new File(filePath);
        if (file.exists()) {
            return file.length();
        }
        return 0;
    }

    /**
     * 检查文件是否存在
     *
     * @param filePath 文件路径
     * @return 是否存在
     */
    public boolean fileExists(String filePath) {
        File file = new File(filePath);
        return file.exists() && file.isFile();
    }

    /**
     * 编码文件名（支持中文）
     *
     * @param filename 原始文件名
     * @return 编码后的文件名
     */
    private String encodeFilename(String filename) {
        try {
            return URLEncoder.encode(filename, StandardCharsets.UTF_8.toString())
                    .replaceAll("\\+", "%20");
        } catch (UnsupportedEncodingException e) {
            log.warn("[FileDownloadService] 文件名编码失败, 使用原始文件名", e);
            return filename;
        }
    }
}
