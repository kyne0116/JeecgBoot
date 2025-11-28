package org.jeecg.modules.ai.config;

import com.alibaba.cloud.ai.agent.studio.loader.AgentLoader;
import com.alibaba.cloud.ai.graph.GraphRepresentation;
import com.alibaba.cloud.ai.graph.agent.BaseAgent;
import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import jakarta.annotation.Nonnull;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Spring AI Alibaba Studio配置
 * 用于解决AgentLoader bean缺失的问题
 *
 * @author JeecgBoot
 * @since 2025-11-28
 */
@Slf4j
@Component
public class AgentStudioConfig implements AgentLoader {

    private final Map<String, BaseAgent> agents = new ConcurrentHashMap<>();

    public AgentStudioConfig(ReactAgent reactAgent) {
        // 打印Agent的图结构(PlantUML格式)
        GraphRepresentation representation = reactAgent.getAndCompileGraph()
                .stateGraph.getGraph(GraphRepresentation.Type.PLANTUML);
        log.info("=== Agent Graph Structure ===");
        log.info(representation.content());
        log.info("=============================");

        // 注册Agent到加载器(使用research_agent名称以兼容Studio UI默认配置)
        this.agents.put("research_agent", reactAgent);
        log.info("✅ Registered agent: research_agent");
    }

    @Override
    @Nonnull
    public List<String> listAgents() {
        return agents.keySet().stream().toList();
    }

    @Override
    public BaseAgent loadAgent(String name) {
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("Agent name cannot be null or empty");
        }

        BaseAgent agent = agents.get(name);
        if (agent == null) {
            throw new NoSuchElementException("Agent not found: " + name);
        }

        return agent;
    }
}