# APIJSON 引入指南

## 概述

本指南详细说明了在 JeecgBoot 项目中引入 APIJSON 依赖的最佳实践和解决方案。APIJSON 是一个开源的 JSON API 框架，托管在 GitHub 上，需要通过 JitPack 仓库进行依赖管理。

## 问题背景

APIJSON 依赖 `com.github.Tencent:APIJSON:8.0.2` 托管在 GitHub 上，需要通过 JitPack.io 仓库下载。由于网络环境或仓库配置问题，可能会出现以下错误：

```
Could not transfer artifact com.github.Tencent:APIJSON:pom:8.0.2 from/to maven-central
Remote host terminated the handshake
```

## 解决方案

### 1. 仓库配置分析

根据 Maven 最佳实践，APIJSON 依赖的仓库配置应该放在**主 pom.xml**中，原因如下：

- APIJSON 依赖在主 pom.xml 的`<dependencies>`和`<dependencyManagement>`中定义
- 父 pom.xml 中的仓库配置会被所有子模块继承
- 避免在多个子模块中重复配置相同的仓库

### 2. 正确的配置位置

**主 pom.xml** (`jeecg-boot/pom.xml`) 中的配置：

```xml
<repositories>
    <!-- 其他仓库配置... -->

    <!-- APIJSON 必须用到的托管平台 -->
    <repository>
        <id>jitpack.io</id>
        <url>https://jitpack.io</url>
        <snapshots>
            <enabled>true</enabled>
        </snapshots>
    </repository>
</repositories>
```

**子模块 pom.xml** 中**不需要**重复配置 JitPack 仓库。

### 3. 依赖配置

在主 pom.xml 中的依赖配置：

```xml
<properties>
    <!-- APIJSON -->
    <apijson.version>8.0.2</apijson.version>
</properties>

<dependencies>
    <!-- APIJSON -->
    <dependency>
        <groupId>com.github.Tencent</groupId>
        <artifactId>APIJSON</artifactId>
    </dependency>
</dependencies>

<dependencyManagement>
    <dependencies>
        <!-- APIJSON -->
        <dependency>
            <groupId>com.github.Tencent</groupId>
            <artifactId>APIJSON</artifactId>
            <version>${apijson.version}</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

## 网络问题解决方案

### 方案一：配置 Maven 镜像

创建或编辑 `~/.m2/settings.xml` 文件：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
          http://maven.apache.org/xsd/settings-1.0.0.xsd">

  <mirrors>
    <!-- 阿里云镜像用于中央仓库 -->
    <mirror>
      <id>alimaven</id>
      <name>aliyun maven</name>
      <url>https://maven.aliyun.com/repository/public</url>
      <mirrorOf>central</mirrorOf>
    </mirror>

    <!-- 不要镜像JitPack，让其使用原始URL -->
  </mirrors>

  <profiles>
    <profile>
      <id>default</id>
      <repositories>
        <repository>
          <id>central</id>
          <url>https://maven.aliyun.com/repository/public</url>
          <releases>
            <enabled>true</enabled>
          </releases>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
        </repository>
        <repository>
          <id>jitpack.io</id>
          <url>https://jitpack.io</url>
          <releases>
            <enabled>true</enabled>
          </releases>
          <snapshots>
            <enabled>true</enabled>
          </snapshots>
        </repository>
      </repositories>
    </profile>
  </profiles>

  <activeProfiles>
    <activeProfile>default</activeProfile>
  </activeProfiles>
</settings>
```

### 方案二：手动安装依赖

如果网络问题持续存在，可以手动下载并安装 APIJSON 依赖：

```bash
# 1. 下载APIJSON依赖文件
curl -L "https://jitpack.io/com/github/Tencent/APIJSON/8.0.2/APIJSON-8.0.2.pom" -o /tmp/APIJSON-8.0.2.pom
curl -L "https://jitpack.io/com/github/Tencent/APIJSON/8.0.2/APIJSON-8.0.2.jar" -o /tmp/APIJSON-8.0.2.jar

# 2. 安装到本地Maven仓库
mvn install:install-file \
  -Dfile=/tmp/APIJSON-8.0.2.jar \
  -DpomFile=/tmp/APIJSON-8.0.2.pom \
  -DgroupId=com.github.Tencent \
  -DartifactId=APIJSON \
  -Dversion=8.0.2 \
  -Dpackaging=jar
```

### 方案三：推送到 Nexus 私服

对于企业环境，推荐将 APIJSON 依赖推送到内部 Nexus 私服，确保团队开发的稳定性：

#### 3.1 推送到 Nexus 私服

```bash
# 1. 下载APIJSON依赖文件
curl -L "https://jitpack.io/com/github/Tencent/APIJSON/8.0.2/APIJSON-8.0.2.pom" -o /tmp/APIJSON-8.0.2.pom
curl -L "https://jitpack.io/com/github/Tencent/APIJSON/8.0.2/APIJSON-8.0.2.jar" -o /tmp/APIJSON-8.0.2.jar

# 2. 推送到Nexus私服（需要配置认证信息）
mvn deploy:deploy-file \
  -Dfile=/tmp/APIJSON-8.0.2.jar \
  -DpomFile=/tmp/APIJSON-8.0.2.pom \
  -DgroupId=com.github.Tencent \
  -DartifactId=APIJSON \
  -Dversion=8.0.2 \
  -Dpackaging=jar \
  -DrepositoryId=nexus-releases \
  -Durl=http://your-nexus-server:8081/repository/maven-releases/
```

#### 3.2 配置 Nexus 认证

在 `~/.m2/settings.xml` 中添加服务器认证信息：

```xml
<settings>
  <servers>
    <server>
      <id>nexus-releases</id>
      <username>your-username</username>
      <password>your-password</password>
    </server>
    <server>
      <id>nexus-snapshots</id>
      <username>your-username</username>
      <password>your-password</password>
    </server>
  </servers>

  <!-- 其他配置... -->
</settings>
```

#### 3.3 配置项目使用私服

修改主 pom.xml，优先使用私服仓库：

```xml
<repositories>
    <!-- 优先使用内部私服 -->
    <repository>
        <id>nexus-public</id>
        <name>Nexus Public Repository</name>
        <url>http://your-nexus-server:8081/repository/maven-public/</url>
        <releases>
            <enabled>true</enabled>
        </releases>
        <snapshots>
            <enabled>true</enabled>
        </snapshots>
    </repository>

    <!-- JitPack作为备用仓库 -->
    <repository>
        <id>jitpack.io</id>
        <url>https://jitpack.io</url>
        <snapshots>
            <enabled>true</enabled>
        </snapshots>
    </repository>
</repositories>
```

#### 3.4 批量推送脚本

创建批量推送脚本 `push-to-nexus.sh`：

```bash
#!/bin/bash

# Nexus服务器配置
NEXUS_URL="http://your-nexus-server:8081"
REPOSITORY_ID="nexus-releases"
RELEASES_URL="${NEXUS_URL}/repository/maven-releases/"

# APIJSON版本配置
APIJSON_VERSION="8.0.2"
GROUP_ID="com.github.Tencent"
ARTIFACT_ID="APIJSON"

# 临时文件目录
TEMP_DIR="/tmp/apijson-deploy"
mkdir -p ${TEMP_DIR}

echo "开始下载APIJSON ${APIJSON_VERSION}..."

# 下载文件
curl -L "https://jitpack.io/${GROUP_ID}/${ARTIFACT_ID}/${APIJSON_VERSION}/${ARTIFACT_ID}-${APIJSON_VERSION}.pom" \
     -o "${TEMP_DIR}/${ARTIFACT_ID}-${APIJSON_VERSION}.pom"

curl -L "https://jitpack.io/${GROUP_ID}/${ARTIFACT_ID}/${APIJSON_VERSION}/${ARTIFACT_ID}-${APIJSON_VERSION}.jar" \
     -o "${TEMP_DIR}/${ARTIFACT_ID}-${APIJSON_VERSION}.jar"

echo "开始推送到Nexus私服..."

# 推送到Nexus
mvn deploy:deploy-file \
  -Dfile="${TEMP_DIR}/${ARTIFACT_ID}-${APIJSON_VERSION}.jar" \
  -DpomFile="${TEMP_DIR}/${ARTIFACT_ID}-${APIJSON_VERSION}.pom" \
  -DgroupId="${GROUP_ID}" \
  -DartifactId="${ARTIFACT_ID}" \
  -Dversion="${APIJSON_VERSION}" \
  -Dpackaging=jar \
  -DrepositoryId="${REPOSITORY_ID}" \
  -Durl="${RELEASES_URL}"

if [ $? -eq 0 ]; then
    echo "✅ APIJSON ${APIJSON_VERSION} 推送成功！"
    echo "🔗 访问地址: ${NEXUS_URL}/#browse/browse:maven-releases"
else
    echo "❌ 推送失败，请检查网络连接和认证配置"
    exit 1
fi

# 清理临时文件
rm -rf ${TEMP_DIR}
echo "🧹 临时文件已清理"
```

使用方法：

```bash
# 给脚本执行权限
chmod +x push-to-nexus.sh

# 执行推送
./push-to-nexus.sh
```

## 验证配置

执行以下命令验证配置是否正确：

```bash
# 清理并编译项目
mvn clean compile

# 如果需要强制更新依赖
mvn clean compile -U
```

成功的编译输出应该显示：

```
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time: XX.XXX s
[INFO] Finished at: YYYY-MM-DD HH:MM:SS
[INFO] ------------------------------------------------------------------------
```

## 最佳实践总结

1. **仓库配置位置**：在主 pom.xml 中配置 JitPack 仓库，避免在子模块中重复配置
2. **依赖管理**：使用`<dependencyManagement>`统一管理版本号
3. **网络优化**：配置合适的 Maven 镜像，但不要镜像 JitPack 仓库
4. **备用方案**：准备手动安装依赖的脚本，应对网络问题
5. **企业环境**：推荐使用 Nexus 私服统一管理第三方依赖，提高构建稳定性
6. **版本控制**：将推送脚本纳入版本控制，便于团队协作和 CI/CD 集成
7. **安全考虑**：使用加密密码或 Token 进行 Nexus 认证，避免明文密码

## 注意事项

### 网络和仓库相关

- JitPack 仓库可能存在网络连接不稳定的情况
- 不要在多个 pom.xml 文件中重复配置相同的仓库
- 建议在 CI/CD 环境中使用手动安装方案或私服确保构建稳定性

### Nexus 私服相关

- 确保 Nexus 服务器有足够的存储空间存放第三方依赖
- 定期备份 Nexus 仓库数据，避免数据丢失
- 配置合适的仓库清理策略，避免存储空间浪费
- 为不同环境（开发、测试、生产）配置不同的仓库策略

### 版本管理

- 定期检查 APIJSON 的新版本更新
- 建立依赖版本升级的测试流程
- 记录依赖变更历史，便于问题追溯

### 安全考虑

- 使用 HTTPS 协议访问 Nexus 私服
- 定期更新 Nexus 服务器和相关组件
- 配置适当的访问权限控制
- 避免在代码中硬编码认证信息

## 相关链接

### 项目相关

- [APIJSON GitHub 仓库](https://github.com/Tencent/APIJSON)
- [JitPack 官网](https://jitpack.io/)

### Maven 相关

- [Maven 仓库配置文档](https://maven.apache.org/guides/mini/guide-multiple-repositories.html)
- [Maven Deploy Plugin 文档](https://maven.apache.org/plugins/maven-deploy-plugin/)
- [Maven Settings 配置参考](https://maven.apache.org/settings.html)

### Nexus 相关

- [Nexus Repository Manager 官网](https://www.sonatype.com/products/nexus-repository)
- [Nexus Repository Manager 文档](https://help.sonatype.com/repomanager3)
- [Nexus REST API 文档](https://help.sonatype.com/repomanager3/integrations/rest-and-integration-api)

---

_本指南基于 JeecgBoot 3.8.1 版本编写，适用于 Java 17 环境。_
