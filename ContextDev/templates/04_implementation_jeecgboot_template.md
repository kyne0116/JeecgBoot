# JeecgBoot 开发实现文档模板 v3.0 - EARS 风格

## 模板说明

本模板采用 **EARS (Easy Approach to Requirements Syntax)** 风格，用自然语言描述开发实现过程，专注于"如何实现"和"实现了什么"。

### EARS 实现语法
```
GIVEN [实现前提] 
WHEN [实现场景]
THEN [实现方案]
WHERE [实现约束]
```

---

## 📋 项目基本信息

**项目名称**: [填写项目名称]  
**开发负责人**: [填写开发负责人]  
**文档创建日期**: [填写日期]  
**开发周期**: [填写开发周期]  
**基于需求文档**: [对应的需求文档名称]  
**基于设计文档**: [对应的设计文档名称]  
**基于任务规划**: [对应的任务规划文档名称]

---

## 🎯 实现目标

### 我们要实现什么？
[用简单语言描述要实现的系统功能]

### 实现要达到什么效果？
- **功能完整**: [所有需求功能都已实现]
- **质量可靠**: [代码质量符合标准]  
- **性能优良**: [系统性能满足要求]

### 实现成功的标准是什么？
- [ ] [可验证的实现标准 1]
- [ ] [可验证的实现标准 2]
- [ ] [可验证的实现标准 3]

---

## 🏗️ 技术架构实现

### 使用了什么技术架构？

#### JeecgBoot 技术栈配置

**GIVEN** 需要快速构建企业级应用  
**WHEN** 选择开发技术栈  
**THEN** 采用JeecgBoot完整技术体系：
- **后端框架**: Spring Boot 3.x + MyBatis-Plus + Spring Security
- **前端框架**: Vue 3 + TypeScript + Ant Design Vue + Vite
- **数据库**: MySQL 8.0+ + Redis缓存
- **开发工具**: Maven 3.9+ + JDK 17
**WHERE** 确保技术栈版本兼容和稳定

#### 系统分层架构实现

**GIVEN** 需要清晰的系统架构  
**WHEN** 设计代码结构  
**THEN** 按以下分层实现：
- **控制层(Controller)**: 处理HTTP请求和响应
- **服务层(Service)**: 实现业务逻辑和事务管理
- **数据层(Mapper)**: 数据访问和持久化操作
- **实体层(Entity)**: 数据模型和对象映射
**WHERE** 各层职责清晰，降低耦合度

---

## 💾 数据库实现

### 数据库如何设计和实现？

#### 数据表结构实现

**GIVEN** 需要存储业务数据  
**WHEN** 设计数据库表结构  
**THEN** 按以下规范实现：

##### 主要业务表: [表名]

```sql
CREATE TABLE `[表名]` (
  `id` varchar(32) NOT NULL COMMENT '主键ID',
  `[业务字段1]` varchar(100) DEFAULT NULL COMMENT '[字段说明]',
  `[业务字段2]` decimal(10,2) DEFAULT NULL COMMENT '[字段说明]',
  `[业务字段3]` datetime DEFAULT NULL COMMENT '[字段说明]',
  `status` tinyint(1) DEFAULT '1' COMMENT '状态(1:正常,0:禁用)',
  `create_by` varchar(32) DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(32) DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `del_flag` tinyint(1) DEFAULT '0' COMMENT '删除标志(0:正常,1:删除)',
  PRIMARY KEY (`id`),
  KEY `idx_[索引名]` (`[字段名]`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='[表说明]';
```

**WHERE** 遵循JeecgBoot数据表命名和字段规范

#### 数据库优化实现

**GIVEN** 需要保证数据库性能  
**WHEN** 优化数据库设计  
**THEN** 实施以下优化措施：
- 为常用查询字段创建索引
- 使用合适的数据类型减少存储空间
- 建立外键约束保证数据一致性
- 设计分区表处理大数据量
**WHERE** 平衡查询性能和存储效率

---

## 🔧 CodeGen代码生成实现

### 如何使用代码生成器？

#### CodeGen配置实现

**GIVEN** 需要快速生成基础CRUD代码  
**WHEN** 配置JeecgBoot代码生成器  
**THEN** 按以下步骤实现：

##### 第一步：数据库表设计确认
- [ ] 数据表结构设计完成
- [ ] 字段类型和约束确认
- [ ] 索引和关系设计完成
- [ ] 表注释和字段注释完整

##### 第二步：代码生成配置
```json
{
  "tableName": "[表名]",
  "entityName": "[实体名]",
  "packageName": "org.jeecg.modules.[模块名]",
  "author": "[开发者姓名]",
  "generateType": "01",
  "tplCategory": "crud",
  "subTableStr": "",
  "relationType": "0"
}
```

##### 第三步：代码生成执行
- [ ] 使用代码生成器生成完整代码
- [ ] 验证生成的Entity实体类
- [ ] 验证生成的Mapper数据访问层
- [ ] 验证生成的Service业务逻辑层
- [ ] 验证生成的Controller控制层
- [ ] 验证生成的Vue前端页面

**WHERE** 确保生成代码的完整性和正确性

#### 生成代码验证

**GIVEN** 代码生成器已生成基础代码  
**WHEN** 验证生成代码质量  
**THEN** 检查以下内容：
- [ ] 实体类注解配置正确
- [ ] 数据访问方法完整
- [ ] 业务逻辑符合规范
- [ ] 控制器接口设计合理
- [ ] 前端页面功能完整
- [ ] 权限注解配置正确

---

## 💻 后端开发实现

### 后端代码如何实现？

#### Entity实体层实现

**GIVEN** 需要定义数据模型  
**WHEN** 创建实体类  
**THEN** 按以下规范实现：

```java
@Data
@TableName("[表名]")
@EqualsAndHashCode(callSuper = false)
@Accessors(chain = true)
@ApiModel(value="[实体名]对象", description="[实体描述]")
public class [实体名] implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.ASSIGN_ID)
    @ApiModelProperty(value = "主键")
    private String id;

    @ApiModelProperty(value = "[字段描述]")
    @ExcelProperty(value = "[字段名]")
    private [字段类型] [字段名];

    @JsonFormat(timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @ApiModelProperty(value = "创建时间")
    private Date createTime;
}
```

**WHERE** 包含必要的注解和序列化接口

#### Service业务层实现

**GIVEN** 需要实现业务逻辑  
**WHEN** 创建业务服务类  
**THEN** 按以下模式实现：

```java
@Service
@Transactional(rollbackFor = Exception.class)
public class [实体名]ServiceImpl extends ServiceImpl<[实体名]Mapper, [实体名]> 
    implements I[实体名]Service {

    @Override
    public IPage<[实体名]> queryPageList(IPage<[实体名]> page, [实体名] entity) {
        // 实现分页查询逻辑
        QueryWrapper<[实体名]> queryWrapper = QueryGenerator.initQueryWrapper(entity, req.getParameterMap());
        return this.page(page, queryWrapper);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void save[实体名](String userId, [实体名] entity) {
        // 实现保存逻辑
        entity.setCreateBy(userId);
        entity.setCreateTime(new Date());
        this.save(entity);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void update[实体名]([实体名] entity) {
        // 实现更新逻辑
        entity.setUpdateTime(new Date());
        this.updateById(entity);
    }
}
```

**WHERE** 包含事务管理和异常处理

#### Controller控制层实现

**GIVEN** 需要提供API接口  
**WHEN** 创建控制器类  
**THEN** 按以下模式实现：

```java
@Api(tags="[功能模块]")
@RestController
@RequestMapping("/[模块路径]")
@Slf4j
public class [实体名]Controller extends JeecgController<[实体名], I[实体名]Service> {

    @Autowired
    private I[实体名]Service [实体名]Service;

    @GetMapping(value = "/list")
    @RequiresPermissions("[权限标识]:list")
    public Result<IPage<[实体名]>> queryPageList([实体名] entity,
                                               @RequestParam(name="pageNo", defaultValue="1") Integer pageNo,
                                               @RequestParam(name="pageSize", defaultValue="10") Integer pageSize,
                                               HttpServletRequest req) {
        // 实现分页查询接口
        QueryWrapper<[实体名]> queryWrapper = QueryGenerator.initQueryWrapper(entity, req.getParameterMap());
        Page<[实体名]> page = new Page<[实体名]>(pageNo, pageSize);
        IPage<[实体名]> pageList = [实体名]Service.page(page, queryWrapper);
        return Result.OK(pageList);
    }

    @PostMapping(value = "/add")
    @RequiresPermissions("[权限标识]:add")
    public Result<String> add(@RequestBody [实体名] entity) {
        // 实现新增接口
        [实体名]Service.save(entity);
        return Result.OK("添加成功！");
    }
}
```

**WHERE** 包含权限控制和统一返回格式

---

## 🎨 前端开发实现

### 前端页面如何实现？

#### Vue 3组件实现

**GIVEN** 需要创建用户界面  
**WHEN** 开发Vue 3组件  
**THEN** 按以下结构实现：

```vue
<template>
  <div>
    <BasicTable @register="registerTable" :rowSelection="rowSelection">
      <template #tableTitle>
        <a-button type="primary" @click="handleAdd" preIcon="ant-design:plus-outlined">
          新增
        </a-button>
        <a-button type="primary" color="warning" @click="onSelectDelete" 
                  preIcon="ant-design:delete-outlined">
          批量删除
        </a-button>
      </template>
      <template #action="{ record }">
        <TableAction
          :actions="[
            { icon: 'clarity:note-edit-line', onClick: handleEdit.bind(null, record) },
            { icon: 'ant-design:delete-outlined', color: 'error', 
              onClick: handleDelete.bind(null, record) },
          ]"
        />
      </template>
    </BasicTable>
    
    <[实体名]Modal @register="registerModal" @success="handleSuccess" />
  </div>
</template>

<script lang="ts" setup>
import { BasicTable, useTable, TableAction } from '/@/components/Table';
import { use[实体名]List, use[实体名]ListColumns } from './hooks/use[实体名]List';
import [实体名]Modal from './components/[实体名]Modal.vue';

const [registerTable, { reload }] = useTable({
  title: '[功能名称]列表',
  api: use[实体名]List,
  columns: use[实体名]ListColumns,
  bordered: true,
  showIndexColumn: false,
  actionColumn: {
    width: 120,
    title: '操作',
    dataIndex: 'action',
    slots: { customRender: 'action' },
  },
});
</script>
```

**WHERE** 使用Ant Design Vue组件和TypeScript

#### API接口集成

**GIVEN** 需要调用后端接口  
**WHEN** 创建API服务  
**THEN** 按以下方式实现：

```typescript
import { defHttp } from '/@/utils/http/axios';

enum [实体名]Api {
  list = '/[模块路径]/list',
  save = '/[模块路径]/add',
  edit = '/[模块路径]/edit',
  delete = '/[模块路径]/delete',
  deleteBatch = '/[模块路径]/deleteBatch',
}

export const get[实体名]List = (params: any) =>
  defHttp.get<any>({ url: [实体名]Api.list, params });

export const save[实体名] = (params: any, isUpdate: boolean) => {
  if (isUpdate) {
    return defHttp.put<any>({ url: [实体名]Api.edit, params });
  } else {
    return defHttp.post<any>({ url: [实体名]Api.save, params });
  }
};

export const delete[实体名] = (params: any) =>
  defHttp.delete<any>({ url: [实体名]Api.delete, params });
```

**WHERE** 包含错误处理和类型定义

---

## 🔐 权限控制实现

### 如何实现权限管理？

#### 后端权限控制

**GIVEN** 需要控制用户访问权限  
**WHEN** 实现权限验证  
**THEN** 在Controller方法上添加权限注解：

```java
@RequiresPermissions("[模块名]:[功能名]:list")
public Result<IPage<Entity>> queryPageList() {
    // 列表查询需要list权限
}

@RequiresPermissions("[模块名]:[功能名]:add")
public Result<String> add(@RequestBody Entity entity) {
    // 新增操作需要add权限
}

@RequiresPermissions("[模块名]:[功能名]:edit")
public Result<String> edit(@RequestBody Entity entity) {
    // 编辑操作需要edit权限
}

@RequiresPermissions("[模块名]:[功能名]:delete")
public Result<String> delete(@RequestParam String id) {
    // 删除操作需要delete权限
}
```

**WHERE** 权限标识遵循统一命名规范

#### 前端权限控制

**GIVEN** 需要控制界面元素显示  
**WHEN** 实现前端权限验证  
**THEN** 使用权限指令和组件：

```vue
<template>
  <!-- 按钮权限控制 -->
  <a-button v-auth="'[模块名]:[功能名]:add'" type="primary">
    新增
  </a-button>
  
  <!-- 菜单权限控制 -->
  <Authority :value="'[模块名]:[功能名]:edit'">
    <a-button type="primary">编辑</a-button>
  </Authority>
</template>

<script lang="ts" setup>
import { Authority } from '/@/components/Authority';
</script>
```

**WHERE** 与后端权限标识保持一致

---

## 🧪 代码质量实现

### 如何保证代码质量？

#### 单元测试实现

**GIVEN** 需要验证代码功能正确性  
**WHEN** 编写单元测试  
**THEN** 为Service层添加测试：

```java
@SpringBootTest
@TestMethodOrder(OrderAnnotation.class)
public class [实体名]ServiceTest {

    @Autowired
    private I[实体名]Service [实体名]Service;

    @Test
    @Order(1)
    public void testSave() {
        [实体名] entity = new [实体名]();
        // 设置测试数据
        entity.set[字段名]("测试数据");
        
        [实体名]Service.save(entity);
        
        assertNotNull(entity.getId());
    }

    @Test
    @Order(2)
    public void testQuery() {
        QueryWrapper<[实体名]> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("[字段名]", "测试数据");
        
        List<[实体名]> list = [实体名]Service.list(queryWrapper);
        
        assertTrue(list.size() > 0);
    }
}
```

**WHERE** 覆盖主要业务逻辑分支

#### 代码规范检查

**GIVEN** 需要统一代码风格  
**WHEN** 执行代码规范检查  
**THEN** 确保以下规范：
- [ ] 类名使用PascalCase命名
- [ ] 方法名使用camelCase命名
- [ ] 常量使用UPPER_SNAKE_CASE命名
- [ ] 包名使用全小写命名
- [ ] 注释完整且有意义
- [ ] 异常处理完善
- [ ] 日志记录适当

---

## ⚡ 性能优化实现

### 如何优化系统性能？

#### 数据库查询优化

**GIVEN** 需要提高查询性能  
**WHEN** 优化数据库操作  
**THEN** 实施以下优化：

```java
// 使用分页查询避免全表扫描
@Override
public IPage<Entity> queryPageList(IPage<Entity> page, Entity entity) {
    QueryWrapper<Entity> wrapper = new QueryWrapper<>();
    
    // 添加必要的查询条件
    if(StringUtils.isNotBlank(entity.getName())) {
        wrapper.like("name", entity.getName());
    }
    
    // 添加排序
    wrapper.orderByDesc("create_time");
    
    return this.page(page, wrapper);
}

// 使用批量操作提高效率
@Override
@Transactional(rollbackFor = Exception.class)
public void saveBatch(List<Entity> entityList) {
    this.saveBatch(entityList, 1000); // 批量大小1000
}
```

**WHERE** 平衡查询精度和性能

#### 缓存实现

**GIVEN** 需要减少数据库访问  
**WHEN** 实现缓存机制  
**THEN** 使用Redis缓存：

```java
@Service
public class [实体名]ServiceImpl extends ServiceImpl<[实体名]Mapper, [实体名]> {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Override
    public [实体名] getById(Serializable id) {
        String cacheKey = "entity:" + id;
        
        // 先从缓存获取
        [实体名] entity = ([实体名]) redisTemplate.opsForValue().get(cacheKey);
        
        if (entity == null) {
            // 缓存未命中，从数据库查询
            entity = super.getById(id);
            if (entity != null) {
                // 存入缓存，设置过期时间
                redisTemplate.opsForValue().set(cacheKey, entity, 30, TimeUnit.MINUTES);
            }
        }
        
        return entity;
    }
}
```

**WHERE** 合理设置缓存过期时间

---

## 🔒 安全实现

### 如何实现系统安全？

#### 输入验证

**GIVEN** 需要防止恶意输入  
**WHEN** 处理用户输入  
**THEN** 实施输入验证：

```java
@PostMapping("/add")
public Result<String> add(@RequestBody @Valid [实体名] entity) {
    // 使用@Valid注解自动验证
    // 在Entity中定义验证规则
    
    // 额外的业务验证
    if (StringUtils.isBlank(entity.getName())) {
        return Result.error("名称不能为空");
    }
    
    // 过滤HTML标签防止XSS
    entity.setName(StringEscapeUtils.escapeHtml4(entity.getName()));
    
    [实体名]Service.save(entity);
    return Result.OK("添加成功");
}
```

**WHERE** 在Entity中定义验证注解

#### SQL注入防护

**GIVEN** 需要防止SQL注入攻击  
**WHEN** 执行数据库查询  
**THEN** 使用参数化查询：

```java
// 正确的做法 - 使用QueryWrapper
QueryWrapper<Entity> wrapper = new QueryWrapper<>();
wrapper.eq("user_id", userId);  // 自动处理参数化
List<Entity> list = this.list(wrapper);

// 或者使用@Param注解
@Select("SELECT * FROM table WHERE user_id = #{userId}")
List<Entity> findByUserId(@Param("userId") String userId);
```

**WHERE** 避免字符串拼接SQL

---

## 📊 监控和日志实现

### 如何实现系统监控？

#### 日志记录

**GIVEN** 需要记录系统运行情况  
**WHEN** 实现日志记录  
**THEN** 使用统一的日志格式：

```java
@Slf4j
@Service
public class [实体名]ServiceImpl {

    @Override
    public void save([实体名] entity) {
        try {
            log.info("开始保存[实体名]，参数：{}", JSON.toJSONString(entity));
            
            // 业务处理
            this.save(entity);
            
            log.info("保存[实体名]成功，ID：{}", entity.getId());
        } catch (Exception e) {
            log.error("保存[实体名]失败，参数：{}，异常：", JSON.toJSONString(entity), e);
            throw new JeecgBootException("保存失败：" + e.getMessage());
        }
    }
}
```

**WHERE** 记录关键操作和异常信息

#### 性能监控

**GIVEN** 需要监控系统性能  
**WHEN** 实现性能监控  
**THEN** 使用AOP记录执行时间：

```java
@Aspect
@Component
@Slf4j
public class PerformanceAspect {

    @Around("@annotation(org.springframework.web.bind.annotation.RequestMapping)")
    public Object around(ProceedingJoinPoint point) throws Throwable {
        long startTime = System.currentTimeMillis();
        
        try {
            Object result = point.proceed();
            long endTime = System.currentTimeMillis();
            
            log.info("方法执行：{}，耗时：{}ms", 
                    point.getSignature().toShortString(), 
                    endTime - startTime);
                    
            return result;
        } catch (Exception e) {
            log.error("方法执行异常：{}，异常：", point.getSignature().toShortString(), e);
            throw e;
        }
    }
}
```

**WHERE** 监控关键接口的执行时间

---

## 🚀 部署配置实现

### 如何配置系统部署？

#### 环境配置

**GIVEN** 需要部署到不同环境  
**WHEN** 配置环境参数  
**THEN** 使用配置文件管理：

```yaml
# application-prod.yml (生产环境)
server:
  port: 8080
  servlet:
    context-path: /jeecg-boot

spring:
  datasource:
    dynamic:
      primary: master
      datasource:
        master:
          url: jdbc:mysql://[生产数据库地址]:3306/jeecg-boot?characterEncoding=UTF-8&useUnicode=true&useSSL=false&tinyInt1isBit=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Shanghai
          username: ${MYSQL_USERNAME:root}
          password: ${MYSQL_PASSWORD:password}
          driver-class-name: com.mysql.cj.jdbc.Driver
  
  redis:
    host: ${REDIS_HOST:127.0.0.1}
    port: ${REDIS_PORT:6379}
    password: ${REDIS_PASSWORD:}
    database: 0
```

**WHERE** 使用环境变量管理敏感信息

#### Docker部署配置

**GIVEN** 需要容器化部署  
**WHEN** 创建Docker配置  
**THEN** 编写Dockerfile：

```dockerfile
FROM openjdk:17-jre-slim

WORKDIR /app

COPY target/jeecg-boot-system-3.5.3.jar app.jar

EXPOSE 8080

ENV JAVA_OPTS="-Xms512m -Xmx1024m"

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

**WHERE** 优化镜像大小和启动时间

---

## ✅ 实现验收

### 如何确认实现质量？

#### 功能实现验收

- [ ] 所有需求功能已实现
- [ ] CodeGen生成代码完整正确
- [ ] 业务逻辑符合需求设计
- [ ] 用户界面友好易用
- [ ] 权限控制正确实施

#### 代码质量验收

- [ ] 代码规范符合标准
- [ ] 单元测试覆盖率达标(≥80%)
- [ ] 集成测试通过
- [ ] 代码审查通过
- [ ] 性能测试达标

#### 安全实现验收

- [ ] 输入验证机制完善
- [ ] SQL注入防护到位
- [ ] XSS攻击防护有效
- [ ] 权限控制严格执行
- [ ] 敏感数据加密存储

#### 部署实现验收

- [ ] 环境配置正确
- [ ] 部署脚本可用
- [ ] 监控日志完善
- [ ] 备份恢复可行
- [ ] 文档说明完整

---

## 📞 联系信息

**开发确认联系人**: [姓名] - [联系方式]  
**技术负责人**: [姓名] - [联系方式]  
**项目经理**: [姓名] - [联系方式]

---

## 📋 文档状态

**文档版本**: v3.0  
**创建日期**: [填写日期]  
**最后更新**: [填写日期]  
**状态**: [开发中/已完成/已测试]  
**下次评审**: [填写日期]

---

## 💡 使用说明

### 如何使用这个实现模板？

1. **明确实现目标**: 基于需求、设计、任务规划确定实现重点
2. **配置技术环境**: 搭建JeecgBoot开发环境和工具链
3. **设计数据结构**: 创建数据库表和实体模型
4. **使用代码生成器**: 快速生成基础CRUD功能代码
5. **扩展业务逻辑**: 在生成代码基础上实现复杂业务
6. **实现前端界面**: 开发用户友好的操作界面
7. **保证代码质量**: 执行测试、规范检查和性能优化
8. **配置部署环境**: 准备生产环境部署配置

### EARS实现格式提示

- **GIVEN**: 描述实现前提条件，开始实现前的状态
- **WHEN**: 描述实现场景，什么情况下执行实现
- **THEN**: 描述实现方案，具体如何实现功能
- **WHERE**: 描述实现约束，有什么限制或特殊要求

### 常见问题

**Q: 如何平衡代码生成和手动开发？**  
A: 优先使用CodeGen生成基础功能，在此基础上扩展复杂业务逻辑

**Q: 如何确保代码质量？**  
A: 建立代码审查机制，执行单元测试，使用静态代码分析工具

**Q: 如何处理复杂业务逻辑？**  
A: 在Service层实现业务逻辑，保持Controller层轻量化，使用设计模式提高可维护性

**注意**: 本文档采用EARS风格，专注于开发实现描述。具体技术细节和最佳实践请参考JeecgBoot官方文档和编程规范。