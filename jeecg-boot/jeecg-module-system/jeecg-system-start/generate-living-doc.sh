#!/bin/bash

# JeecgBoot Living Documentation 生成脚本
echo "🚀 开始生成Living Documentation..."

# 确保在正确的目录
cd "$(dirname "$0")"

# 运行Cucumber测试
echo "📝 执行BDD测试..."
mvn test -Dtest=CucumberTestRunner

# 检查测试是否成功
if [ $? -ne 0 ]; then
    echo "❌ 测试执行失败，无法生成文档"
    exit 1
fi

# 检查JSON报告是否存在
JSON_REPORT="target/cucumber-reports/json/cucumber.json"
if [ ! -f "$JSON_REPORT" ]; then
    echo "❌ 找不到Cucumber JSON报告: $JSON_REPORT"
    exit 1
fi

# 编译并运行Living Doc生成器
echo "📖 生成Living Documentation..."
mvn compile exec:java -Dexec.mainClass="org.jeecg.bdd.LivingDocGenerator" \
    -Dexec.args="$JSON_REPORT target/living-documentation"

# 检查生成是否成功
if [ -f "target/living-documentation/index.html" ]; then
    echo "✅ Living Documentation生成成功!"
    echo "📍 文档位置: target/living-documentation/index.html"
    echo "🌐 在浏览器中打开: file://$(pwd)/target/living-documentation/index.html"
    
    # 在macOS上自动打开
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "target/living-documentation/index.html"
        echo "🎉 已自动在浏览器中打开文档"
    fi
else
    echo "❌ Living Documentation生成失败"
    exit 1
fi