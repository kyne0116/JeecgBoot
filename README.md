# JeecgBoot AI 低代码平台

当前最新版本： 3.8.1（发布日期：2025-06-30）

[![AUR](https://img.shields.io/badge/license-Apache%20License%202.0-blue.svg)](https://github.com/jeecgboot/JeecgBoot/blob/master/LICENSE)
[![](https://img.shields.io/badge/Author-北京国炬软件-orange.svg)](https://jeecg.com)
[![](https://img.shields.io/badge/blog-技术博客-orange.svg)](https://jeecg.blog.csdn.net)
[![](https://img.shields.io/badge/version-3.8.1-brightgreen.svg)](https://github.com/jeecgboot/JeecgBoot)
[![GitHub stars](https://img.shields.io/github/stars/zhangdaiscott/jeecg-boot.svg?style=social&label=Stars)](https://github.com/jeecgboot/JeecgBoot)
[![GitHub forks](https://img.shields.io/github/forks/zhangdaiscott/jeecg-boot.svg?style=social&label=Fork)](https://github.com/jeecgboot/JeecgBoot)

## 项目介绍

<h3 align="center">企业级AI低代码平台</h3>

JeecgBoot 是一款企业级低代码平台集成了 AI 应用平台功能，旨在帮助开发者快速实现低代码开发和构建、部署个性化的 AI 应用。
前后端分离架构 Ant Design4、Vue3，SpringBoot，SpringCloud Alibaba，Mybatis-plus，Shiro/SpringAuthorizationServer，强大的代码生成器让前后端代码一键生成，无需写任何代码；提供强大的报表和大屏工具，满足企业级数据产品需求！
引领 AI 低代码开发模式: AI 生成->OnlineCoding-> 代码生成-> 手工 MERGE， 帮助 Java 项目解决 80%的重复工作，让开发更多关注业务，提高效率、节省成本，同时又不失灵活性！低代码能力：Online 表单、表单设计、流程设计、Online 报表、大屏/仪表盘设计、报表设计; AI 应用平台功能：AI 知识库问答、AI 模型管理、AI 流程编排、AI 聊天等，支持含 ChatGPT、DeepSeek、Ollama 等多种 AI 大模型

`AI赋能低代码:` 提供一套成熟 AI 应用平台功能：包含 AI 应用管理、AI 模型管理、AI 对话助手、AI 知识库问答、AI 流程编排、AI 流程设计器，AI 建表等功能; 支持各种 AI 大模型 ChatGPT、DeepSeek、Ollama、智普、千问等.

`JEECG宗旨是:` 简单功能由 OnlineCoding 零代码搭建，做到`零代码开发`；复杂功能由代码生成器生成进行手工 Merge 实现`低代码开发`，既保证了`智能`又兼顾`灵活`，解决了当前低代码产品普遍不灵活的弊端！

`JEECG业务流程:` 采用工作流来实现、扩展出任务接口，供开发编写业务逻辑，表单提供多种解决方案： 表单设计器、online 配置表单、编码表单。同时实现了流程与表单的分离设计（松耦合）、并支持任务节点灵活配置，既保证了公司流程的保密性，又减少了开发人员的工作量。

## 适用项目

JeecgBoot 低代码平台，可以应用在任何 J2EE 项目的开发中，支持信创国产化。尤其适合 SAAS 项目、企业信息管理系统（MIS）、内部办公系统（OA）、企业资源计划系统（ERP）、客户关系管理系统（CRM）、AI 知识库等，其半智能手工 Merge 的开发方式，可以显著提高开发效率 70%以上，极大降低开发成本。
又是一个全栈式 AI 开发平台，快速帮助企业构建和部署个性化的 AI 应用。

## 🤖 AI 赋能开发环境

JeecgBoot 集成了完整的 AI 赋能开发环境，通过 `jeecg-ai-setup.sh` 安装脚本提供一键式 Context Engineering 和 CodeGen 系统集成。

### 🚀 快速安装

```bash
# 在项目根目录执行
bash ContextDev/jeecg-ai-setup.sh
```

### 📋 核心功能

- **Context Engineering**: 基于 Context Engineering 最佳实践的 AI 编程工作流
- **CodeGen 系统**: 完整的前后端代码自动生成能力，支持单表和复杂业务场景
- **AI 需求分析**: 基于 Code_Gen_Agent.md 的智能业务需求理解和解析
- **示例代码参考**: 完整的 JeecgBoot 后端和前端示例代码集合
- **模板体系**: AI 编程模板集合，包含需求分析、架构设计、测试等

### 🏗️ 安装后目录结构

```
项目根目录/
├── CLAUDE.md                      # 项目级别 AI 编程配置
├── ContextDev/                    # Context Engineering 集成目录
│   ├── templates/                 # AI 编程模板集合
│   └── examples/jeecgboot/        # JeecgBoot 示例代码集合
├── PRPs/                          # AI 工作目录
│   ├── templates/                 # 模板文件
│   └── examples/                  # 示例代码
├── CodeGen/                       # CodeGen 代码生成系统
└── projectDocs/                   # 生成的需求文档输出
```

### ⚡ AI 增强功能

安装完成后，可以使用以下功能：

```bash
# 智能需求文档生成
/jeecg-generate-prp 电商管理系统需求

# 需求文档执行
/jeecg-execute-prp projectDocs/REQUIREMENTS_ecommerce-management.md

# CodeGen 系统直接调用
python3 CodeGen/Code_Gen_Guide.py --help
```

### 🔧 脚本选项

```bash
# 完整安装 Context Engineering 环境
bash ContextDev/jeecg-ai-setup.sh

# 验证安装状态
bash ContextDev/jeecg-ai-setup.sh --verify

# 仅复制示例代码
bash ContextDev/jeecg-ai-setup.sh --examples-only

# 更新 CLAUDE 配置
bash ContextDev/jeecg-ai-setup.sh --update-claude-config
```

### 📚 示例代码参考

安装脚本会自动将 JeecgBoot 示例代码复制到 `PRPs/examples/jeecgboot/`，包含：

- **后端示例**: Entity、Controller、Service、Mapper 完整代码
- **前端示例**: Vue3 组件、API 服务、路由配置
- **架构参考**: JeecgBoot 标准开发模式和最佳实践

AI 在进行代码开发时会自动参考这些示例，确保生成的代码符合 JeecgBoot 规范。

**信创兼容说明**

- 操作系统：国产麒麟、银河麒麟等国产系统几乎都是基于 Linux 内核，因此它们具有良好的兼容性。
- 数据库：达梦、人大金仓、TiDB
- 中间件：东方通 TongWeb、TongRDS，宝兰德 AppServer、CacheDB, [信创配置文档](https://help.jeecg.com/java/tongweb-deploy/)

## 版本说明

| 下载   | JDK17 + SpringBoot2.7                              | JDK17 + SpringBoot3.3 + Shiro                                                 | JDK17 + SpringBoot3.3+ SpringAuthorizationServer                                      |
| ------ | -------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Github | [`master`](https://github.com/jeecgboot/JeecgBoot) | [`springboot3`](https://github.com/jeecgboot/JeecgBoot/tree/springboot3) 分支 | [`springboot3_sas`](https://github.com/jeecgboot/JeecgBoot/tree/springboot3_sas) 分支 |
| Gitee  | [`master`](https://gitee.com/jeecg/JeecgBoot)      | [`springboot3`](https://gitee.com/jeecg/JeecgBoot/tree/springboot3/) 分支     | [`springboot3_sas`](https://gitee.com/jeecg/JeecgBoot/tree/springboot3_sas) 分支      |

- `jeecg-boot` 是后端 JAVA 源码项目（支持单体和微服务切换）.
- `jeecgboot-vue3` 是前端 VUE3 源码项目（vue3+vite6+ts 最新技术栈）.
- `JeecgUniapp` 是[配套 APP 框架](https://github.com/jeecgboot/JeecgUniapp) 适配多个终端，支持 APP、小程序、H5、鸿蒙、鸿蒙 Next.
- 参考 [文档](https://help.jeecg.com/ui/2dev/mini) 可以删除不需要的 demo，制作一个精简版本

## 启动项目

- [IDEA 启动前后端项目](https://help.jeecg.com/java/setup/idea/startup)
- [Docker 一键启动前后端](https://help.jeecg.com/java/docker/quick)

## 技术文档

- 官方网站： [http://www.jeecg.com](http://www.jeecg.com)
- 入门指南： [快速入门](http://www.jeecg.com/doc/quickstart) | [开发文档](https://help.jeecg.com) | [AI 应用使用手册](https://help.jeecg.com/aigc) | [技术博客](https://jeecg.blog.csdn.net)
- 技术支持： [反馈问题](https://github.com/jeecgboot/JeecgBoot/issues/new?template=bug_report.md) | [视频教程](http://jeecg.com/doc/video) | [低代码体验一分钟](https://jeecg.blog.csdn.net/article/details/106079007)
- QQ 交流群 ： 964611995、⑩716488839(满)、⑨808791225(满)、其他(满)

## AI 应用平台介绍

一个全栈式 AI 开发平台，旨在帮助开发者快速构建和部署个性化的 AI 应用。

JeecgBoot 平台提供了一套完善的 AI 应用管理系统模块，是一套类似`Dify`的`AIGC应用开发平台`+`知识库问答`，是一款基于 LLM 大语言模型 AI 应用平台和 RAG 的知识库问答系统。
其直观的界面结合了 AI 流程编排、RAG 管道、知识库管理、模型管理、对接向量库、实时运行可观察等，让您可以快速从原型到生产，拥有 AI 服务能力。

- [详细专题介绍，请点击查看](README-AI.md)

- AI 视频介绍

[![](https://jeecgos.oss-cn-beijing.aliyuncs.com/files/jeecg_aivideo.png)](https://www.bilibili.com/video/BV1zmd7YFE4w)

## 为什么选择 JeecgBoot?

- 1.采用最新主流前后分离框架（Spring Boot + MyBatis + Ant Design4 + Vue3），容易上手；代码生成器依赖性低，灵活的扩展能力，可快速实现二次开发。
- 2.前端大版本换代，最新版采用 Vue3.0 + TypeScript + Vite6 + Ant Design Vue4 等新技术方案。
- 3.支持微服务 Spring Cloud Alibaba（Nacos、Gateway、Sentinel、Skywalking），提供简易机制，支持单体和微服务自由切换（这样可以满足各类项目需求）。
- 4.开发效率高，支持在线建表和 AI 建表，提供强大代码生成器，单表、树列表、一对多、一对一等数据模型，增删改查功能一键生成，菜单配置直接使用。
- 5.代码生成器提供强大模板机制，支持自定义模板，目前提供四套风格模板（单表两套、树模型一套、一对多三套）。
- 6.提供强大的报表和大屏可视化工具，支持丰富的数据源连接，能够通过拖拉拽方式快速制作报表、大屏和门户设计；支持多种图表类型：柱形图、折线图、散点图、饼图、环形图、面积图、漏斗图、进度图、仪表盘、雷达图、地图等。
- 7.低代码能力：在线表单（无需编码，通过在线配置表单，实现表单的增删改查，支持单表、树、一对多、一对一等模型，实现人人皆可编码），在线配置零代码开发、所见即所得支持 23 种类控件。
- 8.低代码能力：在线报表、在线图表（无需编码，通过在线配置方式，实现数据报表和图形报表，可以快速抽取数据，减轻开发压力，实现人人皆可编码）。
- 9.Online 支持在线增强开发，提供在线代码编辑器，支持代码高亮、代码提示等功能，支持多种语言（Java、SQL、JavaScript 等）。
- 10.封装完善的用户、角色、菜单、组织机构、数据字典、在线定时任务等基础功能，支持访问授权、按钮权限、数据权限等功能。
- 11.前端 UI 提供丰富的组件库，支持各种常用组件，如表格、树形控件、下拉框、日期选择器等，满足各种复杂的业务需求 [UI 组件库文档](https://help.jeecg.com/category/ui%E7%BB%84%E4%BB%B6%E5%BA%93)。
- 12.提供 APP 配套框架，一份多代码多终端适配，一份代码多终端适配，小程序、H5、安卓、iOS、鸿蒙 Next。
- 13.新版 APP 框架采用 Uniapp、Vue3.0、Vite、Wot-design-uni、TypeScript 等最新技术栈，包括二次封装组件、路由拦截、请求拦截等功能。实现了与 JeecgBoot 完美对接：目前已经实现登录、用户信息、通讯录、公告、移动首页、九宫格、聊天、Online 表单、仪表盘等功能，提供了丰富的组件。
- 14.提供了一套成熟的 AI 应用平台功能，从 AI 模型、知识库到 AI 应用搭建，助力企业快速落地 AI 服务，加速智能化升级。
- 15.AI 能力：目前 JeecgBoot 支持 AI 大模型 chatgpt 和 deepseek，现在最新版默认使用 deepseek，速度更快质量更高。目前提供了 AI 对话助手、AI 知识库、AI 应用、AI 建表、AI 报表等功能。
- 16.提供新行编辑表格 JVXETable，轻松满足各种复杂 ERP 布局，拥有更高的性能、更灵活的扩展、更强大的功能。
- 17.平台首页风格，提供多种组合模式，支持自定义风格；支持门户设计，支持自定义首页。
- 18.常用共通封装，各种工具类（定时任务、短信接口、邮件发送、Excel 导入导出等），基本满足 80%项目需求。
- 19.简易 Excel 导入导出，支持单表导出和一对多表模式导出，生成的代码自带导入导出功能。
- 20.集成智能报表工具，报表打印、图像报表和数据导出非常方便，可极其方便地生成 PDF、Excel、Word 等报表。
- 21.采用前后分离技术，页面 UI 风格精美，针对常用组件做了封装：时间、行表格控件、截取显示控件、报表组件、编辑器等。
- 22.查询过滤器：查询功能自动生成，后台动态拼 SQL 追加查询条件；支持多种匹配方式（全匹配/模糊查询/包含查询/不匹配查询）。
- 23.数据权限（精细化数据权限控制，控制到行级、列表级、表单字段级，实现不同人看不同数据，不同人对同一个页面操作不同字段）。
- 24.接口安全机制，可细化控制接口授权，非常简便实现不同客户端只看自己数据等控制；也提供了基于 AK 和 SK 认证鉴权的 OpenAPI 功能。
- 25.活跃的社区支持；近年来，随着网络威胁的日益增加，团队在安全和漏洞管理方面积累了丰富的经验，能够为企业提供全面的安全解决方案。
- 26.权限控制采用 RBAC（Role-Based Access Control，基于角色的访问控制）。
- 27.页面校验自动生成（必须输入、数字校验、金额校验、时间空间等）。
- 28.支持 SaaS 服务模式，提供 SaaS 多租户架构方案。
- 29.分布式文件服务，集成 MinIO、阿里 OSS 等优秀的第三方，提供便捷的文件上传与管理，同时也支持本地存储。
- 30.主流数据库兼容，一套代码完全兼容 MySQL、PostgreSQL、Oracle、SQL Server、MariaDB、达梦、人大金仓等主流数据库。
- 31.集成工作流 Flowable，并实现了只需在页面配置流程转向，可极大简化 BPM 工作流的开发；用 BPM 的流程设计器画出了流程走向，一个工作流基本就完成了，只需写很少量的 Java 代码。
- 32.低代码能力：在线流程设计，采用开源 Flowable 流程引擎，实现在线画流程、自定义表单、表单挂靠、业务流转。
- 33.多数据源：极其简易的使用方式，在线配置数据源配置，便捷地从其他数据抓取数据。
- 34.提供单点登录 CAS 集成方案，项目中已经提供完善的对接代码。
- 35.低代码能力：表单设计器，支持用户自定义表单布局，支持单表、一对多表单，支持 select、radio、checkbox、textarea、date、popup、列表、宏等控件。
- 36.专业接口对接机制，统一采用 RESTful 接口方式，集成 Swagger-UI 在线接口文档，JWT token 安全验证，方便客户端对接。
- 37.高级组合查询功能，在线配置支持主子表关联查询，可保存查询历史。
- 38.提供各种系统监控，实时跟踪系统运行情况（监控 Redis、Tomcat、JVM、服务器信息、请求追踪、SQL 监控）。
- 39.消息中心（支持短信、邮件、微信推送等）；集成 WebSocket 消息通知机制。
- 40.支持多语言，提供国际化方案。
- 41.数据变更记录日志，可记录数据每次变更内容，通过版本对比功能查看历史变化。
- 42.提供简单易用的打印插件，支持谷歌、火狐、IE11+等各种浏览器。
- 43.后端采用 Maven 分模块开发方式；前端支持菜单动态路由。
- 44.提供丰富的示例代码，涵盖了常用的业务场景，便于学习和参考。

## 技术架构：

#### 前端

- 前端环境要求：Node.js 要求`Node 20+` 版本以上、pnpm 要求`9+` 版本以上
- 依赖管理：node、npm、pnpm
- 前端 IDE 建议：IDEA、WebStorm、Vscode
- 采用 Vue3.0+TypeScript+Vite6+Ant-Design-Vue4 等新技术方案，包括二次封装组件、utils、hooks、动态菜单、权限校验、按钮级别权限控制等功能
- 最新技术栈：Vue3.0 + TypeScript + Vite6 + ant-design-vue4 + pinia + echarts + unocss + vxe-table + qiankun + es6

#### 后端

- IDE 建议： IDEA (必须安装 lombok 插件 )
- 语言：Java 默认 jdk17(支持 jdk8、jdk21)
- 依赖管理：Maven
- 基础框架：Spring Boot 2.7.18
- 微服务框架： Spring Cloud Alibaba 2021.0.6.2
- 持久层框架：MybatisPlus 3.5.3.2
- 报表工具： JimuReport 1.9.5
- 安全框架：Apache Shiro 1.13.0，Jwt 4.5.0
- 微服务技术栈：Spring Cloud Alibaba、Nacos、Gateway、Sentinel、Skywalking
- 数据库连接池：阿里巴巴 Druid 1.1.24
- AI 大模型：支持 `ChatGPT` `DeepSeek`切换
- 日志打印：logback
- 缓存：Redis
- 其他：autopoi, fastjson，poi，Swagger-ui，quartz, lombok（简化代码）等。
- 默认提供 MySQL5.7+数据库脚本

#### 数据库支持

> jeecgboot 平台支持以下数据库，默认我们只提供 mysql 脚本，其他数据库可以参考[转库文档](https://my.oschina.net/jeecg/blog/4905722)自己转。

| 数据库        | 支持 |
| ------------- | ---- |
| MySQL         | √    |
| Oracle11g     | √    |
| Sqlserver2017 | √    |
| PostgreSQL    | √    |
| MariaDB       | √    |
| 达梦          | √    |
| 人大金仓      | √    |
| TiDB          | √    |
| kingbase8     | √    |

## 微服务解决方案

> 微服务方式快速启动
>
> - [单体快速切换微服务](https://help.jeecg.com/java/springcloud/switchcloud/monomer)
> - [Docker 一键启动微服务前后端](https://help.jeecg.com/java/docker/quickcloud)

- 1、服务注册和发现 Nacos √
- 2、统一配置中心 Nacos √
- 3、路由网关 gateway(三种加载方式) √
- 4、分布式 http feign √
- 5、熔断降级限流 Sentinel √
- 6、分布式文件 Minio、阿里 OSS √
- 7、统一权限控制 JWT + Shiro √
- 8、服务监控 SpringBootAdmin√
- 9、链路跟踪 Skywalking [参考文档](https://help.jeecg.com/java/springcloud/super/skywarking)
- 10、消息中间件 RabbitMQ √
- 11、分布式任务 xxl-job √
- 12、分布式事务 Seata
- 13、轻量分布式日志 Loki+grafana 套件
- 14、支持 docker-compose、k8s、jenkins
- 15、CAS 单点登录 √
- 16、路由限流 √

#### 微服务架构图

![微服务架构图](https://jeecgos.oss-cn-beijing.aliyuncs.com/files/jeecgboot_springcloud2022.png "在这里输入图片标题")

## 开源版与企业版区别?

- JeecgBoot 开源版采用 [Apache-2.0 license](LICENSE) 协议附加补充条款：允许商用使用，不会造成侵权行为，允许基于本平台软件开展业务系统开发（但在任何情况下，您不得使用本软件开发可能被认为与本软件竞争的软件).
- 商业版与开源版主要区别在于商业版提供了技术支持 和 更多的企业级功能(例如：Online 图表、流程监控、流程设计、流程审批、表单设计器、表单视图、积木报表企业版、OA 办公、商业 APP、零代码应用、Online 模块源码等功能). [更多商业功能介绍，点击查看](README-Enterprise.md)
- JeecgBoot 未来发展方向是：零代码平台的建设，也就是团队的另外一款产品 [敲敲云零代码](https://www.qiaoqiaoyun.com) ，无需编码即可通过拖拽快速搭建企业级应用，与 JeecgBoot 低代码平台形成互补，满足从简单业务到复杂系统的全场景开发需求，目前已经上线，[欢迎注册体验](https://app.qiaoqiaoyun.com)

### Jeecg Boot 产品功能蓝图

![功能蓝图](https://jeecgos.oss-cn-beijing.aliyuncs.com/upload/test/Jeecg-Boot-lantu202005_1590912449914.jpg "在这里输入图片标题")

#### 系统功能架构图

![](https://oscimg.oschina.net/oscnet/up-1569487b95a07dbc3599fb1349a2e3aaae1.png)

### 开源版功能清单

```
├─系统管理
│  ├─用户管理
│  ├─角色管理
│  ├─菜单管理
│  ├─权限设置（支持按钮权限、数据权限）
│  ├─表单权限（控制字段禁用、隐藏）
│  ├─部门管理
│  ├─我的部门（二级管理员）
│  └─字典管理
│  └─分类字典
│  └─系统公告
│  └─职务管理
│  └─通讯录
│  ├─多数据源管理
│  └─多租户管理（租户管理、租户角色、我的租户）
├─Online在线开发(低代码)
│  ├─Online在线表单
│  ├─Online代码生成器
│  ├─Online在线报表
│  ├─仪表盘设计器
│  ├─系统编码规则
│  ├─系统校验规则
├─AI应用平台
│  ├─AI知识库问答系统
│  ├─AI大模型管理
│  ├─AI流程编排
│  ├─AI流程设计器
│  ├─AI对话支持图片
│  ├─AI对话助手(智能问答)
│  ├─AI建表（Online表单）
│  ├─AI聊天窗口支持嵌入第三方
│  ├─AI聊天窗口支持移动端
│  ├─支持常见大模型ChatGPT和DeepSeek、ollama等等
│  ├─AI OCR示例
├─积木报表设计器
│  ├─打印设计器
│  ├─数据报表设计
│  ├─图形报表设计（支持echart）
├─消息中心
│  ├─消息管理
│  ├─模板管理
├─代码生成器(低代码)
│  ├─代码生成器功能（一键生成前后端代码，生成后无需修改直接用，绝对是后端开发福音）
│  ├─代码生成器模板（提供4套模板，分别支持单表和一对多模型，不同风格选择）
│  ├─代码生成器模板（生成代码，自带excel导入导出）
│  ├─查询过滤器（查询逻辑无需编码，系统根据页面配置自动生成）
│  ├─高级查询器（弹窗自动组合查询条件）
│  ├─Excel导入导出工具集成（支持单表，一对多 导入导出）
│  ├─平台移动自适应支持
│  ├─提供新版uniapp3的代码生成器模板
├─系统监控
│  ├─基于AK和SK认证鉴权OpenAPI功能
│  ├─Gateway路由网关
│  ├─性能扫描监控
│  │  ├─监控 Redis
│  │  ├─Tomcat
│  │  ├─jvm
│  │  ├─服务器信息
│  │  ├─请求追踪
│  │  ├─磁盘监控
│  ├─定时任务
│  ├─系统日志
│  ├─消息中心（支持短信、邮件、微信推送等等）
│  ├─数据日志（记录数据快照，可对比快照，查看数据变更情况）
│  ├─系统通知
│  ├─SQL监控
│  ├─swagger-ui(在线接口文档)
│─报表示例
│  ├─曲线图
│  └─饼状图
│  └─柱状图
│  └─折线图
│  └─面积图
│  └─雷达图
│  └─仪表图
│  └─进度条
│  └─排名列表
│  └─等等
│─大屏模板
│  ├─作战指挥中心大屏
│  └─物流服务中心大屏
│─常用示例
│  ├─自定义组件
│  ├─对象存储(对接阿里云)
│  ├─JVXETable示例（各种复杂ERP布局示例）
│  ├─单表模型例子
│  └─一对多模型例子
│  └─打印例子
│  └─一对多TAB例子
│  └─内嵌table例子
│  └─常用选择组件
│  └─异步树table
│  └─接口模拟测试
│  └─表格合计示例
│  └─异步树列表示例
│  └─一对多JEditable
│  └─JEditable组件示例
│  └─图片拖拽排序
│  └─图片翻页
│  └─图片预览
│  └─PDF预览
│  └─分屏功能
│─封装通用组件
│  ├─行编辑表格JEditableTable
│  └─省略显示组件
│  └─时间控件
│  └─高级查询
│  └─用户选择组件
│  └─报表组件封装
│  └─字典组件
│  └─下拉多选组件
│  └─选人组件
│  └─选部门组件
│  └─通过部门选人组件
│  └─封装曲线、柱状图、饼状图、折线图等等报表的组件（经过封装，使用简单）
│  └─在线code编辑器
│  └─上传文件组件
│  └─验证码组件
│  └─树列表组件
│  └─表单禁用组件
│  └─等等
│─更多页面模板
│  ├─各种高级表单
│  ├─各种列表效果
│  └─结果页面
│  └─异常页面
│  └─个人页面
├─高级功能
│  ├─提供单点登录CAS集成方案
│  ├─提供APP发布方案
│  ├─集成Websocket消息通知机制
│  ├─支持electron桌面应用打包(支持windows、linux、macOS三大平台)
│  ├─docker容器支持
│  ├─提供移动APP框架及源码（Uniapp3版本）支持H5、小程序、APP、鸿蒙Next
│  ├─提供移动APP低代码设计(Online表单、仪表盘)
```

### 系统效果

##### PC 端

![](https://oscimg.oschina.net/oscnet/up-000530d95df337b43089ac77e562494f454.png)

![输入图片说明](https://static.oschina.net/uploads/img/201904/14155402_AmlV.png "在这里输入图片标题")

![](https://oscimg.oschina.net/oscnet/up-9d6f36f251e71a0b515a01323474b03004c.png)

![输入图片说明](https://static.oschina.net/uploads/img/201904/14160813_KmXS.png "在这里输入图片标题")

![输入图片说明](https://static.oschina.net/uploads/img/201904/14160935_Nibs.png "在这里输入图片标题")

![输入图片说明](https://static.oschina.net/uploads/img/201904/14161004_bxQ4.png "在这里输入图片标题")

##### 系统交互

![](https://oscimg.oschina.net/oscnet/up-78b151fc888d4319377bf1cc311fe826871.png)

![](https://oscimg.oschina.net/oscnet/up-16c07e000278329b69b228ae3189814b8e9.png)

##### AI 功能

AI 聊天助手

![](https://oscimg.oschina.net/oscnet//65298d5710b4e6039a5f802b5f8505c5.png)

AI 建表

![](https://oscimg.oschina.net/oscnet/up-381423599f219a67def45dfd9a99df8ef3f.png)

![](https://oscimg.oschina.net/oscnet/up-1508c2b0708c365605f68893044ee11f20d.png)

AI 写文章

![](https://oscimg.oschina.net/oscnet/up-e3ee5b1fe497308805aa5e324b72994af79.png)

##### 仪表盘设计器

![](https://jeecgos.oss-cn-beijing.aliyuncs.com/files/darg20240726105556.png)

![](https://jeecgos.oss-cn-beijing.aliyuncs.com/files/drag20240724135626.png)

![](https://jeecgos.oss-cn-beijing.aliyuncs.com/files/drag20240724135619.png)

![](https://jeecgos.oss-cn-beijing.aliyuncs.com/files/drag20240724135630.png)

![](https://jeecgos.oss-cn-beijing.aliyuncs.com/files/drag20240726105547.png)

![](https://oscimg.oschina.net/oscnet/up-fad98d42b2cf92f92a903c9cff7579f18ec.png)

##### 报表设计器

![](https://oscimg.oschina.net/oscnet/up-64648de000851f15f6c7b9573d107ebb5f8.png)

![](https://oscimg.oschina.net/oscnet/up-fa52b44445db281c51d3f267dce7450d21b.gif)

![](https://oscimg.oschina.net/oscnet/up-68a19149d640f1646c8ed89ed4375e3326c.png)

![](https://oscimg.oschina.net/oscnet/up-f7e9cb2e3740f2d19ff63b40ec2dd554f96.png)

##### 手机端

![](https://oscimg.oschina.net/oscnet/da543c5d0d57baab0cecaa4670c8b68c521.jpg)
![](https://oscimg.oschina.net/oscnet/fda4bd82cab9d682de1c1fbf2060bf14fa6.jpg)

##### PAD 端

![](https://oscimg.oschina.net/oscnet/e90fef970a8c33790ab03ffd6c4c7cec225.jpg)
![](https://oscimg.oschina.net/oscnet/d78218803a9e856a0aa82b45efc49849a0c.jpg)
![](https://oscimg.oschina.net/oscnet/59c23b230f52384e588ee16309b44fa20de.jpg)

##### 图表示例

![](https://oscimg.oschina.net/oscnet/up-218bc6a1669496b241ebb23506440c0083e.png)

![输入图片说明](https://static.oschina.net/uploads/img/201904/14160834_Lo23.png "在这里输入图片标题")
![输入图片说明](https://static.oschina.net/uploads/img/201904/14160842_QK7B.png "在这里输入图片标题")
![输入图片说明](https://static.oschina.net/uploads/img/201904/14160849_GBm5.png "在这里输入图片标题")
![输入图片说明](https://static.oschina.net/uploads/img/201904/14160858_6RAM.png "在这里输入图片标题")

##### 在线接口文档

![输入图片说明](https://static.oschina.net/uploads/img/201908/27095258_M2Xq.png "在这里输入图片标题")
![输入图片说明](https://static.oschina.net/uploads/img/201904/14160957_hN3X.png "在这里输入图片标题")

##### UNIAPP 效果

![](https://oscimg.oschina.net/oscnet/up-aac943fbd26561879c57a41f7a406edf274.png)

![](https://oscimg.oschina.net/oscnet/up-9a44ba2e82b09c750629d12fafd7f60f553.png)

##### 大屏设计器

![](https://oscimg.oschina.net/oscnet/up-402a6034124474bfef8dfc5b4b2bac1ce5c.png)

![](https://oscimg.oschina.net/oscnet/up-6f7ba2e2ebbeea0d203db8d69fd87644c9f.png)

![](https://oscimg.oschina.net/oscnet/up-ee8d34f318da466b8a6070a6e3111d12ce7.png)

![](https://oscimg.oschina.net/oscnet/up-6b81781b43086819049c4421206810667c5.png)

## 捐赠

如果觉得还不错，请作者喝杯咖啡吧 ☺

![](https://static.oschina.net/uploads/img/201903/08155608_0EFX.png)
