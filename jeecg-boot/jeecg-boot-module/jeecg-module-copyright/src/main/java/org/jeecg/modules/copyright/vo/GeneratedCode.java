package org.jeecg.modules.copyright.vo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * 生成的代码结果
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GeneratedCode {

    /**
     * 源代码文件映射
     * key: 文件路径(相对路径,如com/example/entity/User.java)
     * value: 文件内容
     */
    private Map<String, String> sourceFiles;

    /**
     * 代码质量报告
     */
    private CodeQualityReport qualityReport;

    /**
     * ZIP文件路径(可选)
     */
    private String zipFilePath;

    /**
     * 会话ID
     */
    private String sessionId;
}
