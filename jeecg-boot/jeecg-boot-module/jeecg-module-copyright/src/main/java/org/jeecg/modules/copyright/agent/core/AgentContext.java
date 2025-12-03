package org.jeecg.modules.copyright.agent.core;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.jeecg.modules.copyright.vo.CopyrightRequirement;

import java.util.HashMap;
import java.util.Map;

/**
 * Agent执行上下文
 * 用于在Agent执行过程中传递必要的上下文信息
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AgentContext {

    /**
     * 会话ID
     */
    private String sessionId;

    /**
     * 用户ID
     */
    private String userId;

    /**
     * 软著需求对象(由ReactClarifyAgent澄清后生成)
     */
    private CopyrightRequirement requirement;

    /**
     * 工作目录(文件生成目录)
     */
    private String workDir;

    /**
     * 线程ID(用于ReactAgent多轮对话上下文管理)
     */
    private String threadId;

    /**
     * 扩展参数Map(用于传递额外信息)
     */
    @Builder.Default
    private Map<String, Object> params = new HashMap<>();

    /**
     * 元数据Map(用于存储Agent执行过程中的临时数据)
     */
    @Builder.Default
    private Map<String, Object> metadata = new HashMap<>();

    /**
     * 添加扩展参数
     */
    public void putParam(String key, Object value) {
        this.params.put(key, value);
    }

    /**
     * 获取扩展参数
     */
    public <T> T getParam(String key, Class<T> clazz) {
        Object value = this.params.get(key);
        return clazz.cast(value);
    }

    /**
     * 添加元数据
     */
    public void putMetadata(String key, Object value) {
        this.metadata.put(key, value);
    }

    /**
     * 获取元数据
     */
    public <T> T getMetadata(String key, Class<T> clazz) {
        Object value = this.metadata.get(key);
        return clazz.cast(value);
    }
}
