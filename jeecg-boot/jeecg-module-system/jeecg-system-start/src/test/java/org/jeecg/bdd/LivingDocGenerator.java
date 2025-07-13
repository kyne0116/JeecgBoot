package org.jeecg.bdd;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

/**
 * Living Documentation生成器
 * 将Cucumber JSON报告转换为可读的业务文档
 */
public class LivingDocGenerator {
    
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("用法: java LivingDocGenerator <cucumber.json路径> <输出目录>");
            System.exit(1);
        }
        
        String jsonPath = args[0];
        String outputDir = args[1];
        
        try {
            generateLivingDocumentation(jsonPath, outputDir);
            System.out.println("✅ Living Documentation生成成功: " + outputDir + "/index.html");
        } catch (Exception e) {
            System.err.println("❌ 生成Living Documentation失败: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    public static void generateLivingDocumentation(String jsonPath, String outputDir) throws IOException {
        // 创建输出目录
        Files.createDirectories(Paths.get(outputDir));
        
        // 读取并解析JSON报告
        String jsonContent = Files.readString(Paths.get(jsonPath));
        JsonNode features = objectMapper.readTree(jsonContent);
        
        // 生成HTML文档
        StringBuilder html = new StringBuilder();
        html.append(generateHtmlHeader());
        
        for (JsonNode feature : features) {
            html.append(generateFeatureSection(feature));
        }
        
        html.append(generateHtmlFooter());
        
        // 写入文件
        try (FileWriter writer = new FileWriter(outputDir + "/index.html")) {
            writer.write(html.toString());
        }
        
        // 复制样式文件
        generateCssFile(outputDir);
    }
    
    private static String generateHtmlHeader() {
        return """
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>JeecgBoot系统 - Living Documentation</title>
                <link rel="stylesheet" href="styles.css">
            </head>
            <body>
                <div class="container">
                    <header class="header">
                        <h1>🚀 JeecgBoot系统业务需求文档</h1>
                        <p class="subtitle">基于BDD测试自动生成的实时文档</p>
                        <div class="meta-info">
                            <span>📅 生成时间: """ + 
                LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")) + 
                """
                            </span>
                            <span>🔄 状态: 与代码实时同步</span>
                        </div>
                    </header>
                    <nav class="toc">
                        <h2>📑 目录</h2>
                        <ul id="toc-list"></ul>
                    </nav>
                    <main class="content">
            """;
    }
    
    private static String generateFeatureSection(JsonNode feature) {
        StringBuilder section = new StringBuilder();
        
        String featureName = feature.get("name").asText();
        String description = feature.has("description") ? 
            feature.get("description").asText().trim() : "";
        
        section.append(String.format("""
            <section class="feature" id="feature-%s">
                <h2 class="feature-title">🎯 %s</h2>
                <div class="feature-description">%s</div>
                <div class="scenarios">
            """, 
            featureName.replaceAll("\\s+", "-").toLowerCase(),
            featureName,
            formatDescription(description)
        ));
        
        // 处理场景
        JsonNode elements = feature.get("elements");
        if (elements != null) {
            for (JsonNode element : elements) {
                if ("scenario".equals(element.get("type").asText()) || 
                    "scenario".equals(element.get("keyword").asText())) {
                    section.append(generateScenarioSection(element));
                }
            }
        }
        
        section.append("</div></section>");
        return section.toString();
    }
    
    private static String generateScenarioSection(JsonNode scenario) {
        String scenarioName = scenario.get("name").asText();
        String status = getScenarioStatus(scenario);
        String statusClass = status.equals("passed") ? "success" : 
                           status.equals("failed") ? "error" : "warning";
        String statusIcon = status.equals("passed") ? "✅" : 
                           status.equals("failed") ? "❌" : "⚠️";
        
        StringBuilder scenarioHtml = new StringBuilder();
        scenarioHtml.append(String.format("""
            <div class="scenario %s">
                <h3 class="scenario-title">
                    %s %s
                    <span class="status-badge %s">%s</span>
                </h3>
                <div class="steps">
            """, 
            statusClass, statusIcon, scenarioName, statusClass, status.toUpperCase()
        ));
        
        // 处理步骤
        JsonNode steps = scenario.get("steps");
        if (steps != null) {
            for (JsonNode step : steps) {
                scenarioHtml.append(generateStepSection(step));
            }
        }
        
        scenarioHtml.append("</div></div>");
        return scenarioHtml.toString();
    }
    
    private static String generateStepSection(JsonNode step) {
        String keyword = step.get("keyword").asText();
        String name = step.get("name").asText();
        
        JsonNode result = step.get("result");
        String status = result != null ? result.get("status").asText() : "undefined";
        String duration = result != null && result.has("duration") ? 
            formatDuration(result.get("duration").asLong()) : "";
        
        String statusIcon = status.equals("passed") ? "✅" : 
                           status.equals("failed") ? "❌" : 
                           status.equals("skipped") ? "⏭️" : "❓";
        
        return String.format("""
            <div class="step step-%s">
                <span class="step-keyword">%s</span>
                <span class="step-name">%s</span>
                <span class="step-status">%s</span>
                <span class="step-duration">%s</span>
            </div>
            """, 
            status, keyword, name, statusIcon, duration
        );
    }
    
    private static String getScenarioStatus(JsonNode scenario) {
        JsonNode steps = scenario.get("steps");
        if (steps == null) return "undefined";
        
        boolean allPassed = true;
        boolean hasFailed = false;
        
        for (JsonNode step : steps) {
            JsonNode result = step.get("result");
            if (result != null) {
                String status = result.get("status").asText();
                if ("failed".equals(status)) {
                    hasFailed = true;
                    break;
                } else if (!"passed".equals(status)) {
                    allPassed = false;
                }
            }
        }
        
        return hasFailed ? "failed" : (allPassed ? "passed" : "partial");
    }
    
    private static String formatDuration(long nanoseconds) {
        if (nanoseconds < 1_000_000) {
            return String.format("%.2fms", nanoseconds / 1_000_000.0);
        } else if (nanoseconds < 1_000_000_000) {
            return String.format("%.0fms", nanoseconds / 1_000_000.0);
        } else {
            return String.format("%.1fs", nanoseconds / 1_000_000_000.0);
        }
    }
    
    private static String formatDescription(String description) {
        if (description.isEmpty()) return "";
        
        return "<div class=\"description\">" + 
               description.replaceAll("\\n", "<br>") + 
               "</div>";
    }
    
    private static String generateHtmlFooter() {
        return """
                    </main>
                    <footer class="footer">
                        <p>📋 本文档由JeecgBoot BDD测试自动生成</p>
                        <p>🔄 每次测试运行后自动更新，确保与实际功能保持一致</p>
                    </footer>
                </div>
                <script>
                    // 生成目录
                    document.addEventListener('DOMContentLoaded', function() {
                        const tocList = document.getElementById('toc-list');
                        const features = document.querySelectorAll('.feature');
                        
                        features.forEach(feature => {
                            const title = feature.querySelector('.feature-title').textContent;
                            const id = feature.id;
                            const li = document.createElement('li');
                            li.innerHTML = `<a href="#${id}">${title}</a>`;
                            tocList.appendChild(li);
                        });
                    });
                </script>
            </body>
            </html>
            """;
    }
    
    private static void generateCssFile(String outputDir) throws IOException {
        String css = """
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f8f9fa;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                border-radius: 10px;
                margin-bottom: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .subtitle {
                font-size: 1.2em;
                opacity: 0.9;
                margin-bottom: 20px;
            }
            
            .meta-info {
                display: flex;
                justify-content: center;
                gap: 20px;
                font-size: 0.9em;
            }
            
            .toc {
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .toc h2 {
                margin-bottom: 15px;
                color: #495057;
            }
            
            .toc ul {
                list-style: none;
            }
            
            .toc li {
                margin-bottom: 8px;
            }
            
            .toc a {
                color: #667eea;
                text-decoration: none;
                padding: 5px 10px;
                display: block;
                border-radius: 4px;
                transition: background-color 0.3s;
            }
            
            .toc a:hover {
                background-color: #f8f9fa;
            }
            
            .feature {
                background: white;
                margin-bottom: 30px;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .feature-title {
                background: #495057;
                color: white;
                padding: 20px;
                margin: 0;
                font-size: 1.5em;
            }
            
            .feature-description {
                padding: 20px;
                background: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
            
            .scenarios {
                padding: 20px;
            }
            
            .scenario {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                margin-bottom: 20px;
                overflow: hidden;
            }
            
            .scenario.success {
                border-left: 4px solid #28a745;
            }
            
            .scenario.error {
                border-left: 4px solid #dc3545;
            }
            
            .scenario.warning {
                border-left: 4px solid #ffc107;
            }
            
            .scenario-title {
                padding: 15px 20px;
                background: #f8f9fa;
                margin: 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .status-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.8em;
                font-weight: bold;
            }
            
            .status-badge.success {
                background: #d4edda;
                color: #155724;
            }
            
            .status-badge.error {
                background: #f8d7da;
                color: #721c24;
            }
            
            .status-badge.warning {
                background: #fff3cd;
                color: #856404;
            }
            
            .steps {
                padding: 20px;
            }
            
            .step {
                display: flex;
                align-items: center;
                padding: 8px 0;
                border-bottom: 1px solid #f8f9fa;
            }
            
            .step:last-child {
                border-bottom: none;
            }
            
            .step-keyword {
                font-weight: bold;
                color: #495057;
                min-width: 60px;
                margin-right: 10px;
            }
            
            .step-name {
                flex: 1;
                margin-right: 10px;
            }
            
            .step-status {
                margin-right: 10px;
            }
            
            .step-duration {
                font-size: 0.9em;
                color: #6c757d;
                min-width: 60px;
                text-align: right;
            }
            
            .footer {
                text-align: center;
                padding: 30px;
                color: #6c757d;
                border-top: 1px solid #dee2e6;
                margin-top: 40px;
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
                
                .header {
                    padding: 20px;
                }
                
                .header h1 {
                    font-size: 2em;
                }
                
                .meta-info {
                    flex-direction: column;
                    gap: 10px;
                }
                
                .step {
                    flex-direction: column;
                    align-items: flex-start;
                }
                
                .step-duration {
                    text-align: left;
                }
            }
            """;
        
        try (FileWriter writer = new FileWriter(outputDir + "/styles.css")) {
            writer.write(css);
        }
    }
}