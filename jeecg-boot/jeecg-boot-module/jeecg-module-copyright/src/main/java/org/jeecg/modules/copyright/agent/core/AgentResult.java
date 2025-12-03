package org.jeecg.modules.copyright.agent.core;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Agent执行结果
 * 封装Agent执行后的结果信息
 *
 * @author Claude Code
 * @since 2025-12-02
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AgentResult {

    /**
     * 执行是否成功
     */
    private boolean success;

    /**
     * 结果消息(成功或失败的描述)
     */
    private String message;

    /**
     * 具体结果数据(可能是CopyrightRequirement、QualityCheckReport等)
     */
    private Object data;

    /**
     * 生成的文件路径列表
     */
    @Builder.Default
    private List<String> generatedFiles = new ArrayList<>();

    /**
     * 元数据Map(存储Token消耗、执行时长等信息)
     */
    @Builder.Default
    private Map<String, Object> metadata = new HashMap<>();

    /**
     * 错误堆栈(仅在失败时填充)
     */
    private String errorStack;

    /**
     * 创建成功结果(快捷方法)
     */
    public static AgentResult success(String message) {
        return AgentResult.builder()
                .success(true)
                .message(message)
                .build();
    }

    /**
     * 创建成功结果(带数据)
     */
    public static AgentResult success(String message, Object data) {
        return AgentResult.builder()
                .success(true)
                .message(message)
                .data(data)
                .build();
    }

    /**
     * 创建失败结果
     */
    public static AgentResult failure(String message) {
        return AgentResult.builder()
                .success(false)
                .message(message)
                .build();
    }

    /**
     * 创建失败结果(带错误堆栈)
     */
    public static AgentResult failure(String message, String errorStack) {
        return AgentResult.builder()
                .success(false)
                .message(message)
                .errorStack(errorStack)
                .build();
    }

    /**
     * 添加生成的文件
     */
    public void addGeneratedFile(String filePath) {
        this.generatedFiles.add(filePath);
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
        return value != null ? clazz.cast(value) : null;
    }
}
