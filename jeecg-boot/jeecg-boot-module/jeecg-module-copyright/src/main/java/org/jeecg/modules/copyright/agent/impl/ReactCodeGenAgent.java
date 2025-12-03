package org.jeecg.modules.copyright.agent.impl;

import cn.hutool.json.JSONUtil;
import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import lombok.extern.slf4j.Slf4j;
import org.jeecg.modules.copyright.agent.core.*;
import org.jeecg.modules.copyright.agent.tools.CodeQualityChecker;
import org.jeecg.modules.copyright.agent.tools.CodeZipPackager;
import org.jeecg.modules.copyright.vo.*;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.model.ToolContext;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.function.FunctionToolCallback;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;
import java.util.function.BiFunction;

/**
 * ReactCodeGenAgent - 代码生成Agent
 * <p>
 * 基于用户需求自动生成5000-6000行Java源代码,包含完整的MVC结构
 *
 * @author Claude Code
 * @since 2025-12-03
 */
@Component
@Slf4j
public class ReactCodeGenAgent implements CopyrightAgent {

    @Autowired
    private ChatModel chatModel;

    @Autowired
    private BiFunction<GeneratedCode, ToolContext, CodeQualityReport> codeQualityChecker;

    @Autowired
    private CodeZipPackager codeZipPackager;

    private static final String AGENT_INSTRUCTION = """
            你是一个专业的Java代码生成专家。你的任务是根据软著申报需求,生成5000-6000行有效Java代码。

            代码要求:
            1. 技术栈: Spring Boot 3.x + MyBatis-Plus
            2. 代码结构: 必须包含完整的MVC架构
               - Entity层(实体类)
               - Mapper层(DAO接口)
               - Service层(业务逻辑)
               - Controller层(接口控制器)
               - VO层(视图对象)
               - Util层(工具类)
            3. 代码行数: 有效代码行数必须在5000-6000行之间
            4. 代码质量: 符合阿里巴巴Java开发规范
            5. 功能完整: 每个功能模块都要有完整的CRUD操作

            生成步骤:
            1. 根据需求分析,确定需要生成的功能模块
            2. 为每个功能模块生成完整的Entity、Mapper、Service、Controller
            3. 生成必要的VO类、工具类、配置类
            4. 调用checkCodeQuality工具检查代码质量
            5. 如果代码行数不足5000行,增加功能模块或完善现有代码
            6. 如果代码行数超过6000行,精简冗余代码
            7. 重复步骤4-6,直到代码行数符合要求

            代码模板示例:
            - Entity: 使用@Data、@TableName等注解
            - Mapper: 继承BaseMapper<T>
            - Service: 接口+实现类分离
            - Controller: RESTful风格,包含@Api注解

            注意事项:
            - 所有代码必须可编译通过
            - 包名统一使用org.jeecg.modules.{软件英文名}
            - 每个类都要有完整的JavaDoc注释
            - 业务逻辑要合理,不要生成无意义的代码
            - 最终必须调用checkCodeQuality工具验证代码质量
            """;

    @Override
    @LogAgentExecution
    public AgentResult execute(AgentContext context) {
        log.info("[ReactCodeGenAgent] 开始执行代码生成, sessionId: {}", context.getSessionId());

        try {
            CopyrightRequirement requirement = context.getRequirement();
            if (requirement == null) {
                return AgentResult.failure("需求信息不能为空");
            }

            // 构建ReactAgent
            ReactAgent reactAgent = buildReactAgent(context);

            // 准备生成提示词
            String generationPrompt = buildGenerationPrompt(requirement);

            log.info("[ReactCodeGenAgent] 开始生成代码...");

            // TODO: 调用reactAgent.invoke()执行代码生成
            // 当前返回模拟结果
            Map<String, String> sourceFiles = generateMockCode(requirement);

            // 进行代码质量检查
            GeneratedCode generatedCode = GeneratedCode.builder()
                    .sourceFiles(sourceFiles)
                    .sessionId(context.getSessionId())
                    .build();

            CodeQualityReport qualityReport = codeQualityChecker.apply(generatedCode, null);

            // 打包ZIP
            String zipFilePath = codeZipPackager.packageSourceCode(sourceFiles, context.getSessionId());

            generatedCode.setQualityReport(qualityReport);
            generatedCode.setZipFilePath(zipFilePath);

            log.info("[ReactCodeGenAgent] 代码生成完成 - 有效行数:{}, ZIP路径:{}",
                    qualityReport.getEffectiveLines(), zipFilePath);

            return AgentResult.success("代码生成完成", generatedCode);

        } catch (Exception e) {
            log.error("[ReactCodeGenAgent] 代码生成失败", e);
            return AgentResult.failure("代码生成失败: " + e.getMessage());
        }
    }

    /**
     * 构建ReactAgent实例
     */
    private ReactAgent buildReactAgent(AgentContext context) {
        log.info("[ReactCodeGenAgent] 开始构建ReactAgent");

        // 将代码质量检查器包装为ToolCallback
        ToolCallback qualityCheckTool = FunctionToolCallback.builder(
                "checkCodeQuality",
                codeQualityChecker
        )
        .description("检查生成代码的质量,包括代码行数、结构完整性等。返回质量报告和优化建议。")
        .inputType(GeneratedCode.class)
        .build();

        // 使用ReactAgent.builder()构建Agent
        ReactAgent agent = (ReactAgent) ReactAgent.builder()
                .name("ReactCodeGenAgent")
                .description("Java代码生成Agent,根据软著申报需求生成5000-6000行源代码")
                .instruction(AGENT_INSTRUCTION)
                .model(chatModel)
                .tools(qualityCheckTool)
                .build();

        log.info("[ReactCodeGenAgent] ReactAgent构建完成");
        return agent;
    }

    /**
     * 构建代码生成提示词
     */
    private String buildGenerationPrompt(CopyrightRequirement requirement) {
        return String.format("""
                请为以下软件项目生成完整的Java源代码:

                软件名称: %s
                软件简称: %s
                版本号: %s
                软件分类: %s
                编程语言: %s
                技术架构: %s

                核心功能:
                %s

                技术创新点:
                %s

                请生成5000-6000行有效Java代码,包含完整的实体、DAO、Service、Controller层。
                """,
                requirement.getSoftwareName(),
                requirement.getShortName(),
                requirement.getVersion(),
                requirement.getCategory(),
                requirement.getCodeLanguage(),
                requirement.getTechStack(),
                JSONUtil.toJsonStr(requirement.getFeatures()),
                JSONUtil.toJsonStr(requirement.getInnovations())
        );
    }

    /**
     * 生成模拟代码(用于测试)
     * TODO: 实际应该由LLM生成
     */
    private Map<String, String> generateMockCode(CopyrightRequirement requirement) {
        Map<String, String> sourceFiles = new HashMap<>();

        String basePackage = "org/jeecg/modules/" + requirement.getShortName().toLowerCase();

        // 生成实体类示例
        String entityCode = generateEntityClass(requirement);
        sourceFiles.put(basePackage + "/entity/User.java", entityCode);

        // 生成Mapper接口示例
        String mapperCode = generateMapperClass(requirement);
        sourceFiles.put(basePackage + "/mapper/UserMapper.java", mapperCode);

        // 生成Service接口和实现类示例
        String serviceInterfaceCode = generateServiceInterface(requirement);
        sourceFiles.put(basePackage + "/service/IUserService.java", serviceInterfaceCode);

        String serviceImplCode = generateServiceImpl(requirement);
        sourceFiles.put(basePackage + "/service/impl/UserServiceImpl.java", serviceImplCode);

        // 生成Controller示例
        String controllerCode = generateControllerClass(requirement);
        sourceFiles.put(basePackage + "/controller/UserController.java", controllerCode);

        log.info("[ReactCodeGenAgent] 生成模拟代码文件数量: {}", sourceFiles.size());

        return sourceFiles;
    }

    private String generateEntityClass(CopyrightRequirement requirement) {
        String basePackage = "org.jeecg.modules." + requirement.getShortName().toLowerCase();
        String authorName = requirement.getApplicant() != null ? requirement.getApplicant().getName() : "Auto Generated";
        return String.format("""
                package %s.entity;

                import com.baomidou.mybatisplus.annotation.IdType;
                import com.baomidou.mybatisplus.annotation.TableId;
                import com.baomidou.mybatisplus.annotation.TableName;
                import lombok.Data;
                import java.io.Serializable;
                import java.util.Date;

                /**
                 * 用户实体类
                 * @author %s
                 * @since %s
                 */
                @Data
                @TableName("sys_user")
                public class User implements Serializable {
                    private static final long serialVersionUID = 1L;

                    @TableId(type = IdType.ASSIGN_ID)
                    private String id;

                    private String username;

                    private String password;

                    private String realname;

                    private String email;

                    private String phone;

                    private Integer status;

                    private Date createTime;

                    private Date updateTime;

                    // 省略getter/setter方法...
                }
                """,
                basePackage,
                authorName,
                requirement.getVersion()
        );
    }

    private String generateMapperClass(CopyrightRequirement requirement) {
        String basePackage = "org.jeecg.modules." + requirement.getShortName().toLowerCase();
        String authorName = requirement.getApplicant() != null ? requirement.getApplicant().getName() : "Auto Generated";
        return String.format("""
                package %s.mapper;

                import com.baomidou.mybatisplus.core.mapper.BaseMapper;
                import %s.entity.User;
                import org.apache.ibatis.annotations.Mapper;

                /**
                 * 用户Mapper接口
                 * @author %s
                 * @since %s
                 */
                @Mapper
                public interface UserMapper extends BaseMapper<User> {
                    // 自定义查询方法可以在这里添加
                }
                """,
                basePackage,
                basePackage,
                authorName,
                requirement.getVersion()
        );
    }

    private String generateServiceInterface(CopyrightRequirement requirement) {
        String basePackage = "org.jeecg.modules." + requirement.getShortName().toLowerCase();
        String authorName = requirement.getApplicant() != null ? requirement.getApplicant().getName() : "Auto Generated";
        return String.format("""
                package %s.service;

                import com.baomidou.mybatisplus.extension.service.IService;
                import %s.entity.User;

                /**
                 * 用户服务接口
                 * @author %s
                 * @since %s
                 */
                public interface IUserService extends IService<User> {
                    // 自定义业务方法
                }
                """,
                basePackage,
                basePackage,
                authorName,
                requirement.getVersion()
        );
    }

    private String generateServiceImpl(CopyrightRequirement requirement) {
        String basePackage = "org.jeecg.modules." + requirement.getShortName().toLowerCase();
        String authorName = requirement.getApplicant() != null ? requirement.getApplicant().getName() : "Auto Generated";
        return String.format("""
                package %s.service.impl;

                import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
                import %s.entity.User;
                import %s.mapper.UserMapper;
                import %s.service.IUserService;
                import org.springframework.stereotype.Service;

                /**
                 * 用户服务实现类
                 * @author %s
                 * @since %s
                 */
                @Service
                public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements IUserService {
                    // 业务逻辑实现
                }
                """,
                basePackage,
                basePackage,
                basePackage,
                basePackage,
                authorName,
                requirement.getVersion()
        );
    }

    private String generateControllerClass(CopyrightRequirement requirement) {
        String basePackage = "org.jeecg.modules." + requirement.getShortName().toLowerCase();
        String authorName = requirement.getApplicant() != null ? requirement.getApplicant().getName() : "Auto Generated";
        return String.format("""
                package %s.controller;

                import %s.entity.User;
                import %s.service.IUserService;
                import org.jeecg.common.api.vo.Result;
                import org.springframework.beans.factory.annotation.Autowired;
                import org.springframework.web.bind.annotation.*;

                /**
                 * 用户控制器
                 * @author %s
                 * @since %s
                 */
                @RestController
                @RequestMapping("/api/user")
                public class UserController {

                    @Autowired
                    private IUserService userService;

                    @GetMapping("/list")
                    public Result<?> list() {
                        return Result.OK(userService.list());
                    }

                    @PostMapping("/add")
                    public Result<?> add(@RequestBody User user) {
                        userService.save(user);
                        return Result.OK("添加成功");
                    }

                    @PutMapping("/edit")
                    public Result<?> edit(@RequestBody User user) {
                        userService.updateById(user);
                        return Result.OK("编辑成功");
                    }

                    @DeleteMapping("/delete")
                    public Result<?> delete(@RequestParam String id) {
                        userService.removeById(id);
                        return Result.OK("删除成功");
                    }
                }
                """,
                basePackage,
                basePackage,
                basePackage,
                authorName,
                requirement.getVersion()
        );
    }

    @Override
    public String getAgentName() {
        return "ReactCodeGenAgent";
    }

    @Override
    public AgentType getAgentType() {
        return AgentType.REACT_AGENT;
    }
}
