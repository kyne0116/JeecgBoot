package org.jeecg.modules.ai.controller;

import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import org.jeecg.common.api.vo.Result;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 自定义Agent控制器
 * 重命名为CustomAgentController以避免与Studio的AgentController冲突
 */
@Controller
@RequestMapping("/ai/chat")
public class ChatAgentController {

    private final ReactAgent reactAgent;
    private final ChatModel chatModel;
    private final Map<String, Object> threadStates = new ConcurrentHashMap<>();

    public ChatAgentController(ReactAgent reactAgent, ChatModel chatModel) {
        this.reactAgent = reactAgent;
        this.chatModel = chatModel;
    }

    @GetMapping("/invoke")
    @ResponseBody
    public Result<?> invoke(@RequestParam("query") String query,
                         @RequestParam("threadId") String threadId
    ) {
        try {
            // 直接使用ChatModel调用(简化版,不使用工具)
            var response = chatModel.call(new Prompt(query));
            String responseMessage = response.getResult().getOutput().getText();

            return Result.ok(responseMessage);
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("Agent处理失败: " + e.getMessage());
        }
    }

    @GetMapping(value = "/stream", produces = "text/event-stream")
    @ResponseBody
    public SseEmitter stream(@RequestParam("query") String query,
                            @RequestParam("threadId") String threadId) {
        SseEmitter emitter = new SseEmitter(60000L);

        // 异步处理
        new Thread(() -> {
            try {
                // 调用ChatModel的stream方法
                var flux = chatModel.stream(new Prompt(query));

                // 订阅并发送流式数据
                flux.subscribe(
                    chatResponse -> {
                        try {
                            String content = chatResponse.getResult().getOutput().getText();
                            if (content != null && !content.isEmpty()) {
                                emitter.send(SseEmitter.event()
                                    .data(content)
                                    .name("message"));
                            }
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    },
                    error -> {
                        try {
                            emitter.send(SseEmitter.event()
                                .data("错误: " + error.getMessage())
                                .name("error"));
                            emitter.complete();
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    },
                    () -> {
                        try {
                            emitter.send(SseEmitter.event()
                                .data("[DONE]")
                                .name("done"));
                            emitter.complete();
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                );
            } catch (Exception e) {
                try {
                    emitter.send(SseEmitter.event()
                        .data("错误: " + e.getMessage())
                        .name("error"));
                    emitter.completeWithError(e);
                } catch (Exception ex) {
                    ex.printStackTrace();
                }
            }
        }).start();

        return emitter;
    }

    @GetMapping
    public String index() {
        return "index";
    }
}
