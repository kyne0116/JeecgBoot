package org.jeecg.modules.ai.controller;

import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import com.alibaba.fastjson.JSONObject;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.common.api.vo.Result;
import org.jeecg.modules.ai.vo.EventData;
import org.jeecg.modules.ai.vo.EventErrorData;
import org.jeecg.modules.ai.vo.EventMessageData;
import org.springframework.ai.chat.messages.Message;
import org.springframework.ai.chat.messages.SystemMessage;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * AI Chat 控制器 - 企业级 SSE 流式聊天实现
 * 参考 JeecgBoot airag 模块设计
 *
 * 主要特性：
 * 1. 线程池管理 - 避免无限创建线程
 * 2. 缓存管理 - 支持断线重连
 * 3. 结构化事件 - 统一的事件数据格式
 * 4. 错误处理 - 友好的错误提示
 * 5. 停止机制 - 支持中断请求
 *
 * @author admin
 * @date 2024/12/03
 */
@Slf4j
@Controller
@RequestMapping("/ai/chat")
public class ChatAgentController {

    private final ReactAgent reactAgent;
    private final ChatModel chatModel;

    /**
     * 固定线程池 - 最多10个并发请求
     */
    private static final ExecutorService SSE_THREAD_POOL = Executors.newFixedThreadPool(10);

    /**
     * SseEmitter 缓存 - 用于管理活跃连接
     * Key: requestId
     * Value: SseEmitter
     */
    private final Map<String, SseEmitter> emitterCache = new ConcurrentHashMap<>();

    /**
     * 历史消息缓存 - 用于断线重连
     * Key: requestId
     * Value: List<EventData>
     */
    private final Map<String, List<EventData>> historyMsgCache = new ConcurrentHashMap<>();

    /**
     * 停止标志缓存 - 用于中断请求
     * Key: requestId
     * Value: AtomicBoolean (true表示需要停止)
     */
    private final Map<String, AtomicBoolean> stopFlagCache = new ConcurrentHashMap<>();

    public ChatAgentController(ReactAgent reactAgent, ChatModel chatModel) {
        this.reactAgent = reactAgent;
        this.chatModel = chatModel;
    }

    /**
     * 同步调用接口 - 非流式
     *
     * @param query 用户查询
     * @param threadId 线程ID
     * @return Result 包含AI响应
     */
    @GetMapping("/invoke")
    @ResponseBody
    public Result<?> invoke(@RequestParam("query") String query,
                            @RequestParam("threadId") String threadId) {
        try {
            log.info("[AI-Chat] 同步调用 - query={}, threadId={}", query, threadId);

            // 使用带时间上下文的Prompt
            Prompt promptWithTime = buildPromptWithTimeContext(query);
            var response = chatModel.call(promptWithTime);
            String responseMessage = response.getResult().getOutput().getText();

            log.info("[AI-Chat] 同步调用完成 - response length={}", responseMessage.length());
            return Result.ok(responseMessage);
        } catch (Exception e) {
            log.error("[AI-Chat] 同步调用失败", e);
            return Result.error("Agent处理失败: " + e.getMessage());
        }
    }

    /**
     * 流式调用接口 - SSE
     *
     * @param query 用户查询
     * @param threadId 线程ID（会话标识）
     * @return SseEmitter SSE发射器
     */
    @GetMapping(value = "/stream", produces = "text/event-stream")
    @ResponseBody
    public SseEmitter stream(@RequestParam("query") String query,
                             @RequestParam("threadId") String threadId) {
        // 生成唯一请求ID
        String requestId = UUID.randomUUID().toString();
        log.info("[AI-Chat] 开始流式调用 - requestId={}, query={}, threadId={}", requestId, query, threadId);

        // 创建 SSE Emitter（永不超时，由客户端控制）
        SseEmitter emitter = createSSE(requestId);

        // 缓存 emitter 和历史消息列表
        emitterCache.put(requestId, emitter);
        historyMsgCache.put(requestId, new CopyOnWriteArrayList<>());
        stopFlagCache.put(requestId, new AtomicBoolean(false));

        // 发送初始化事件（返回 requestId 给客户端）
        EventData initEvent = new EventData(requestId, EventData.EVENT_INIT_REQUEST_ID, requestId);
        sendMessage2Client(emitter, requestId, initEvent);

        // 使用线程池异步处理
        SSE_THREAD_POOL.execute(() -> {
            try {
                log.info("[AI-Chat] 开始调用LLM - requestId={}", requestId);

                // 使用带时间上下文的Prompt调用stream方法
                Prompt promptWithTime = buildPromptWithTimeContext(query);
                var flux = chatModel.stream(promptWithTime);

                // 订阅并发送流式数据
                flux.subscribe(
                    chatResponse -> {
                        // 检查是否需要停止
                        if (stopFlagCache.getOrDefault(requestId, new AtomicBoolean(false)).get()) {
                            log.warn("[AI-Chat] 请求已被停止 - requestId={}", requestId);
                            return;
                        }

                        // 检查连接是否还活跃
                        if (!emitterCache.containsKey(requestId)) {
                            log.debug("[AI-Chat] 客户端已断开连接，停止发送 - requestId={}", requestId);
                            return;
                        }

                        try {
                            String content = chatResponse.getResult().getOutput().getText();
                            if (content != null && !content.isEmpty()) {
                                // 发送消息事件
                                EventData messageEvent = new EventData(
                                    requestId,
                                    EventData.EVENT_MESSAGE,
                                    EventMessageData.builder()
                                        .message(content)
                                        .messageType("text")
                                        .isComplete(false)
                                        .build()
                                );
                                sendMessage2Client(emitter, requestId, messageEvent);
                            }
                        } catch (IllegalStateException e) {
                            // 连接已关闭，静默处理（客户端断开是正常行为）
                            log.debug("[AI-Chat] 客户端已断开连接 - requestId={}", requestId);
                            cleanupCache(requestId);
                        } catch (Exception e) {
                            log.error("[AI-Chat] 发送消息失败 - requestId={}", requestId, e);
                        }
                    },
                    error -> {
                        // 错误处理
                        log.error("[AI-Chat] LLM调用异常 - requestId={}", requestId, error);

                        String errMsg = error.getMessage();
                        if (errMsg != null && errMsg.contains("timeout")) {
                            errMsg = "当前用户较多，排队中，请稍后再试！";
                        } else {
                            errMsg = "调用大模型接口失败: " + errMsg;
                        }

                        EventData errorEvent = new EventData(
                            requestId,
                            EventData.EVENT_ERROR,
                            EventErrorData.builder()
                                .success(false)
                                .message(errMsg)
                                .errorType("model_error")
                                .detail(error.getMessage())
                                .build()
                        );
                        sendMessage2Client(emitter, requestId, errorEvent);
                        closeSSE(emitter, requestId);
                    },
                    () -> {
                        // 完成处理
                        log.info("[AI-Chat] LLM调用完成 - requestId={}", requestId);

                        EventData endEvent = new EventData(
                            requestId,
                            EventData.EVENT_MESSAGE_END,
                            EventMessageData.builder()
                                .message("[DONE]")
                                .isComplete(true)
                                .build()
                        );
                        closeSSE(emitter, requestId, endEvent);
                    }
                );
            } catch (Exception e) {
                log.error("[AI-Chat] 流式调用异常 - requestId={}", requestId, e);

                EventData errorEvent = new EventData(
                    requestId,
                    EventData.EVENT_ERROR,
                    EventErrorData.builder()
                        .success(false)
                        .message("调用大模型接口失败: " + e.getMessage())
                        .errorType("system_error")
                        .detail(e.getMessage())
                        .build()
                );
                sendMessage2Client(emitter, requestId, errorEvent);
                closeSSE(emitter, requestId);
            }
        });

        return emitter;
    }

    /**
     * 断线重连接口 - 继续接收历史消息
     *
     * @param requestId 请求ID
     * @return SseEmitter 新的SSE连接
     */
    @GetMapping(value = "/receive/{requestId}")
    @ResponseBody
    public SseEmitter receiveByRequestId(@PathVariable(name = "requestId") String requestId) {
        log.info("[AI-Chat] 断线重连 - requestId={}", requestId);

        // 检查主线程SSE是否还在
        if (!emitterCache.containsKey(requestId)) {
            log.warn("[AI-Chat] 断线重连失败 - 主连接已关闭, requestId={}", requestId);
            return null;
        }

        // 获取历史消息
        List<EventData> historyMsg = historyMsgCache.get(requestId);
        if (historyMsg == null || historyMsg.isEmpty()) {
            log.warn("[AI-Chat] 断线重连失败 - 无历史消息, requestId={}", requestId);
            return null;
        }

        // 创建新的 emitter
        SseEmitter emitter = createSSE(requestId);

        // 120秒超时
        final long timeoutMillis = 120_000L;

        // 使用线程池异步推送历史消息
        SSE_THREAD_POOL.submit(() -> {
            int lastIndex = 0;
            long lastActiveTime = System.currentTimeMillis();

            try {
                while (true) {
                    if (lastIndex < historyMsg.size()) {
                        // 有新消息 - 发送
                        try {
                            EventData eventData = historyMsg.get(lastIndex++);
                            String eventStr = JSONObject.toJSONString(eventData);
                            log.debug("[AI-Chat] 断线重连-推送消息: requestId={}, eventType={}",
                                requestId, eventData.getEventType());

                            emitter.send(SseEmitter.event().data(eventStr));

                            // 重置超时计时
                            lastActiveTime = System.currentTimeMillis();
                        } catch (IOException e) {
                            log.error("[AI-Chat] 断线重连-发送消息失败: requestId={}", requestId, e);
                            break;
                        }
                    } else {
                        // 没有新消息
                        if (!emitterCache.containsKey(requestId)) {
                            // 主线程SSE已结束 - 退出
                            log.info("[AI-Chat] 断线重连-主连接已关闭，退出: requestId={}", requestId);
                            break;
                        } else if (System.currentTimeMillis() - lastActiveTime > timeoutMillis) {
                            // 等待超时 - 退出
                            log.warn("[AI-Chat] 断线重连-等待超时，退出: requestId={}", requestId);
                            break;
                        } else {
                            // 未超时 - 休眠等待新消息
                            Thread.sleep(500);
                        }
                    }
                }
            } catch (Exception e) {
                log.error("[AI-Chat] 断线重连异常: requestId={}", requestId, e);
            } finally {
                try {
                    emitter.complete();
                } catch (Exception ignore) {}
            }
        });

        return emitter;
    }

    /**
     * 停止请求接口
     *
     * @param requestId 请求ID
     * @return Result 停止结果
     */
    @GetMapping(value = "/stop/{requestId}")
    @ResponseBody
    public Result<?> stop(@PathVariable(name = "requestId") String requestId) {
        log.info("[AI-Chat] 停止请求 - requestId={}", requestId);

        AtomicBoolean stopFlag = stopFlagCache.get(requestId);
        if (stopFlag == null) {
            log.warn("[AI-Chat] 停止请求失败 - 请求不存在, requestId={}", requestId);
            return Result.error("请求不存在或已完成");
        }

        // 设置停止标志
        stopFlag.set(true);

        // 获取 emitter 并关闭
        SseEmitter emitter = emitterCache.get(requestId);
        if (emitter != null) {
            EventData stopEvent = new EventData(
                requestId,
                EventData.EVENT_MESSAGE_END,
                EventMessageData.builder()
                    .message("用户已停止")
                    .isComplete(true)
                    .build()
            );
            closeSSE(emitter, requestId, stopEvent);
        }

        log.info("[AI-Chat] 停止请求成功 - requestId={}", requestId);
        return Result.ok("已停止");
    }

    /**
     * 首页 - 测试页面
     *
     * @return 视图名称
     */
    @GetMapping
    public String index() {
        return "index";
    }

    // ==================== 私有方法 ====================

    /**
     * 构建带时间上下文的Prompt
     *
     * @param userQuery 用户查询
     * @return Prompt 包含系统时间消息和用户消息
     */
    private Prompt buildPromptWithTimeContext(String userQuery) {
        // 获取当前时间并格式化
        LocalDateTime now = LocalDateTime.now();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy年MM月dd日 HH:mm:ss EEEE");
        String currentTime = now.format(formatter);

        // 构建系统消息 - 注入时间上下文
        String systemContent = String.format(
            "当前时间是：%s\n" +
            "请在回答问题时，如果涉及时间相关的查询，请基于上述时间进行计算和回答。",
            currentTime
        );

        SystemMessage systemMessage = new SystemMessage(systemContent);
        UserMessage userMessage = new UserMessage(userQuery);

        // 返回包含系统消息和用户消息的Prompt
        return new Prompt(List.of(systemMessage, userMessage));
    }

    /**
     * 创建 SSE Emitter
     *
     * @param requestId 请求ID
     * @return SseEmitter
     */
    private SseEmitter createSSE(String requestId) {
        // -0L 表示永不超时（由客户端控制）
        SseEmitter emitter = new SseEmitter(-0L);

        // 错误回调 - 清理缓存
        emitter.onError(throwable -> {
            log.warn("[AI-Chat] SSE错误 - requestId={}, error={}", requestId, throwable.getMessage());
            cleanupCache(requestId);
            try {
                emitter.complete();
            } catch (Exception ignore) {}
        });

        // 完成回调 - 清理缓存
        emitter.onCompletion(() -> {
            log.info("[AI-Chat] SSE完成 - requestId={}", requestId);
            cleanupCache(requestId);
        });

        return emitter;
    }

    /**
     * 发送消息到客户端
     *
     * @param emitter SSE发射器
     * @param requestId 请求ID
     * @param eventData 事件数据
     */
    private void sendMessage2Client(SseEmitter emitter, String requestId, EventData eventData) {
        try {
            // 序列化事件数据
            String eventStr = JSONObject.toJSONString(eventData);
            log.debug("[AI-Chat] 发送消息 - requestId={}, eventType={}", requestId, eventData.getEventType());

            // 发送 SSE 事件
            emitter.send(SseEmitter.event().data(eventStr));

            // 缓存历史消息（用于断线重连）
            List<EventData> historyMsg = historyMsgCache.get(requestId);
            if (historyMsg != null) {
                historyMsg.add(eventData);
            }
        } catch (IllegalStateException e) {
            // 连接已关闭，静默处理（客户端断开是正常行为）
            log.debug("[AI-Chat] 连接已关闭，停止发送 - requestId={}", requestId);
            throw e; // 重新抛出，让调用方知道连接已关闭
        } catch (IOException e) {
            log.error("[AI-Chat] 发送消息IO异常 - requestId={}", requestId, e);
            throw new IllegalStateException("IO exception while sending message", e);
        }
    }

    /**
     * 关闭 SSE 连接
     *
     * @param emitter SSE发射器
     * @param requestId 请求ID
     */
    private void closeSSE(SseEmitter emitter, String requestId) {
        closeSSE(emitter, requestId, null);
    }

    /**
     * 关闭 SSE 连接
     *
     * @param emitter SSE发射器
     * @param requestId 请求ID
     * @param finalEvent 最终事件（可选）
     */
    private void closeSSE(SseEmitter emitter, String requestId, EventData finalEvent) {
        if (emitter == null) {
            log.warn("[AI-Chat] 关闭SSE失败 - emitter为null, requestId={}", requestId);
            return;
        }

        try {
            // 发送最终事件
            if (finalEvent != null) {
                sendMessage2Client(emitter, requestId, finalEvent);
            }
        } catch (Exception e) {
            if (!e.getMessage().contains("ResponseBodyEmitter has already completed")) {
                log.error("[AI-Chat] 关闭SSE时发送最终事件失败 - requestId={}", requestId, e);
            }
        } finally {
            // 清理缓存
            cleanupCache(requestId);

            // 关闭 emitter
            try {
                emitter.complete();
            } catch (Exception ignore) {}
        }
    }

    /**
     * 清理缓存
     *
     * @param requestId 请求ID
     */
    private void cleanupCache(String requestId) {
        emitterCache.remove(requestId);
        stopFlagCache.remove(requestId);

        // 延迟清理历史消息（5分钟后），以支持断线重连
        SSE_THREAD_POOL.execute(() -> {
            try {
                Thread.sleep(5 * 60 * 1000); // 5分钟
                historyMsgCache.remove(requestId);
                log.debug("[AI-Chat] 清理历史消息缓存 - requestId={}", requestId);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
    }
}
