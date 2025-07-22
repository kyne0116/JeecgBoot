# JeecgBoot 示例代码库结构

## 📁 目录结构 (添加到 Context Engineering 的 examples/ 目录)

```
examples/
├── jeecg-boot/
│   ├── README.md                    # JeecgBoot 示例说明
│   ├── codegen/                     # CodeGen 系统示例
│   │   ├── Code_Gen_Guide.json      # 表单模板配置示例
│   │   ├── Code_Gen_field_templates.json  # 字段模板示例
│   │   ├── ai_generated_configs/    # AI 生成的配置示例
│   │   │   ├── employee_config.json
│   │   │   ├── customer_config.json
│   │   │   └── product_config.json
│   │   └── workflow_examples/       # 工作流示例
│   │       ├── simple_crud.md
│   │       ├── online_form.md
│   │       └── complex_module.md
│   ├── backend/
│   │   ├── entity/
│   │   │   └── Employee.java        # 标准实体类示例
│   │   ├── mapper/
│   │   │   └── EmployeeMapper.java  # MyBatis-Plus Mapper 示例
│   │   ├── service/
│   │   │   ├── IEmployeeService.java
│   │   │   └── impl/
│   │   │       └── EmployeeServiceImpl.java
│   │   ├── controller/
│   │   │   └── EmployeeController.java  # REST Controller 示例
│   │   └── config/
│   │       └── CodeGenConfig.json   # 代码生成配置示例
│   ├── frontend/
│   │   ├── views/
│   │   │   └── employee/
│   │   │       ├── index.vue        # 列表页面示例
│   │   │       └── components/
│   │   │           ├── EmployeeModal.vue  # 弹窗表单示例
│   │   │           └── EmployeeDetail.vue # 详情页面示例
│   │   ├── api/
│   │   │   └── employee.ts          # API接口定义示例
│   │   └── types/
│   │       └── employee.ts          # TypeScript类型定义
│   ├── database/
│   │   ├── schema.sql               # 数据库表结构示例
│   │   └── data.sql                 # 测试数据示例
│   └── tests/
│       ├── unit/
│       │   └── EmployeeServiceTest.java
│       ├── integration/
│       │   └── EmployeeControllerTest.java
│       └── e2e/
│           └── employee.spec.ts
```

## 📝 关键示例文件内容

### backend/entity/Employee.java

```java
@Data
@TableName("hrms_employee")
@ApiModel(value="Employee", description="员工信息")
public class Employee extends BaseEntity {

    @ApiModelProperty(value = "工号")
    @Excel(name = "工号", width = 15)
    private String employeeNo;

    @ApiModelProperty(value = "姓名")
    @Excel(name = "姓名", width = 15)
    private String name;

    @ApiModelProperty(value = "部门ID")
    private String deptId;

    @ApiModelProperty(value = "职位ID")
    private String positionId;

    // 继承BaseEntity包含7个系统字段
}
```

### backend/controller/EmployeeController.java

```java
@RestController
@RequestMapping("/api/hrms/employee")
@Slf4j
@Api(tags="员工管理")
public class EmployeeController extends JeecgController<Employee, IEmployeeService> {

    @AutoLog(value = "员工管理-分页列表查询")
    @ApiOperation(value="员工管理-分页列表查询", notes="员工管理-分页列表查询")
    @GetMapping(value = "/list")
    @RequiresPermissions("hrms:employee:list")
    public Result<IPage<Employee>> queryPageList(Employee employee,
                                               @RequestParam(name="pageNo", defaultValue="1") Integer pageNo,
                                               @RequestParam(name="pageSize", defaultValue="10") Integer pageSize,
                                               HttpServletRequest req) {
        QueryWrapper<Employee> queryWrapper = QueryGenerator.initQueryWrapper(employee, req.getParameterMap());
        Page<Employee> page = new Page<Employee>(pageNo, pageSize);
        IPage<Employee> pageList = employeeService.page(page, queryWrapper);
        return Result.OK(pageList);
    }

    @AutoLog(value = "员工管理-添加")
    @ApiOperation(value="员工管理-添加", notes="员工管理-添加")
    @PostMapping(value = "/add")
    @RequiresPermissions("hrms:employee:add")
    public Result<String> add(@RequestBody Employee employee) {
        employeeService.save(employee);
        return Result.OK("添加成功！");
    }
}
```

### frontend/views/employee/index.vue

```vue
<template>
  <div>
    <div class="table-page-search-wrapper">
      <a-form layout="inline" @keyup.enter.native="searchQuery">
        <a-row :gutter="24">
          <a-col :xl="6" :lg="7" :md="8" :sm="24">
            <a-form-item label="工号">
              <a-input
                placeholder="请输入工号"
                v-model:value="queryParam.employeeNo"
              ></a-input>
            </a-form-item>
          </a-col>
          <a-col :xl="6" :lg="7" :md="8" :sm="24">
            <a-form-item label="姓名">
              <a-input
                placeholder="请输入姓名"
                v-model:value="queryParam.name"
              ></a-input>
            </a-form-item>
          </a-col>
          <a-col :xl="6" :lg="7" :md="8" :sm="24">
            <span class="table-page-search-submitButtons">
              <a-button type="primary" @click="searchQuery" icon="search"
                >查询</a-button
              >
              <a-button
                type="primary"
                @click="searchReset"
                icon="reload"
                style="margin-left: 8px"
                >重置</a-button
              >
            </span>
          </a-col>
        </a-row>
      </a-form>
    </div>

    <div class="table-operator">
      <a-button
        @click="handleAdd"
        type="primary"
        icon="plus"
        v-auth="'hrms:employee:add'"
        >新增</a-button
      >
      <a-button
        type="primary"
        icon="download"
        @click="handleExportXls('员工信息')"
        >导出</a-button
      >
      <a-upload
        name="file"
        :showUploadList="false"
        :multiple="false"
        :headers="tokenHeader"
        :action="importExcelUrl"
        @change="handleImportExcel"
        v-auth="'hrms:employee:import'"
      >
        <a-button type="primary" icon="import">导入</a-button>
      </a-upload>
    </div>

    <a-table
      ref="table"
      size="middle"
      :scroll="{ x: true }"
      bordered
      rowKey="id"
      :columns="columns"
      :dataSource="dataSource"
      :pagination="ipagination"
      :loading="loading"
      :rowSelection="rowSelection"
      class="j-table-force-nowrap"
      @change="handleTableChange"
    >
      <template #htmlSlot="{ text }">
        <div v-html="text"></div>
      </template>
      <template #imgSlot="{ text }">
        <span v-if="!text" style="font-size: 12px;font-style: italic;"
          >无图片</span
        >
        <img
          v-else
          :src="getImgView(text)"
          height="25px"
          alt=""
          style="max-width:80px;font-size: 12px;font-style: italic;"
        />
      </template>
      <template #fileSlot="{ text }">
        <span v-if="!text" style="font-size: 12px;font-style: italic;"
          >无文件</span
        >
        <a-button
          v-else
          :ghost="true"
          type="primary"
          icon="download"
          size="small"
          @click="downloadFile(text)"
        >
          下载
        </a-button>
      </template>

      <template #action="{ record }">
        <a @click="handleEdit(record)" v-auth="'hrms:employee:edit'">编辑</a>
        <a-divider type="vertical" />
        <a-dropdown>
          <a class="ant-dropdown-link">更多 <DownOutlined /></a>
          <template #overlay>
            <a-menu>
              <a-menu-item>
                <a @click="handleDetail(record)">详情</a>
              </a-menu-item>
              <a-menu-item>
                <a-popconfirm
                  title="确定删除吗?"
                  @confirm="() => handleDelete(record.id)"
                  v-auth="'hrms:employee:delete'"
                >
                  <a>删除</a>
                </a-popconfirm>
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </template>
    </a-table>

    <EmployeeModal ref="modalForm" @ok="modalFormOk"></EmployeeModal>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, unref, onMounted } from "vue";
import { DownOutlined } from "@ant-design/icons-vue";
import { useListPage } from "/@/hooks/system/useListPage";
import EmployeeModal from "./components/EmployeeModal.vue";
import { columns } from "./employee.data";
import {
  list,
  deleteOne,
  batchDelete,
  getImportUrl,
  getExportUrl,
} from "./employee.api";

const checkedKeys = ref<Array<string | number>>([]);
//注册table数据
const { prefixCls, tableContext, onExportXls, onImportXls } = useListPage({
  tableProps: {
    title: "员工管理",
    api: list,
    columns,
    canResize: false,
    formConfig: {
      //labelWidth: 120,
      schemas: [
        {
          label: "工号",
          field: "employeeNo",
          component: "Input",
          colProps: { span: 6 },
        },
        {
          label: "姓名",
          field: "name",
          component: "Input",
          colProps: { span: 6 },
        },
      ],
    },
    actionColumn: {
      width: 120,
      fixed: "right",
    },
  },
  exportConfig: {
    name: "员工信息",
    url: getExportUrl,
  },
  importConfig: {
    url: getImportUrl,
  },
});

//获取表格实例
const [registerTable, { reload }, { rowSelection, selectedRowKeys }] =
  tableContext;

const modalForm = ref();

/**
 * 新增事件
 */
function handleAdd() {
  modalForm.value.disableSubmit = false;
  modalForm.value.edit({});
}

/**
 * 编辑事件
 */
function handleEdit(record: Recordable) {
  modalForm.value.disableSubmit = false;
  modalForm.value.edit(record);
}

/**
 * 详情
 */
function handleDetail(record: Recordable) {
  modalForm.value.disableSubmit = true;
  modalForm.value.edit(record);
}

/**
 * 删除事件
 */
async function handleDelete(id) {
  await deleteOne({ id }, handleSuccess);
}

/**
 * 批量删除事件
 */
async function batchHandleDelete() {
  await batchDelete({ ids: selectedRowKeys.value }, handleSuccess);
}

/**
 * 成功回调
 */
function handleSuccess() {
  (selectedRowKeys.value as any[]) = [];
  reload();
}

/**
 * 操作栏
 */
function getTableAction(record) {
  return [
    {
      label: "编辑",
      onClick: handleEdit.bind(null, record),
      auth: "hrms:employee:edit",
    },
  ];
}

/**
 * 下拉操作栏
 */
function getDropDownAction(record) {
  return [
    {
      label: "详情",
      onClick: handleDetail.bind(null, record),
    },
    {
      label: "删除",
      popConfirm: {
        title: "是否确认删除",
        confirm: handleDelete.bind(null, record),
        placement: "topLeft",
      },
      auth: "hrms:employee:delete",
    },
  ];
}

function modalFormOk() {
  handleSuccess();
}
</script>
```

## 🔧 配置文件示例

### Code_Gen_Config.json (员工管理示例)

```json
{
  "head": {
    "tableName": "hrms_employee",
    "tableTxt": "员工信息",
    "tableType": "1",
    "formCategory": "bdfl_ptbd"
  },
  "fields": [
    {
      "dbFieldName": "id",
      "dbFieldTxt": "主键",
      "dbType": "VARCHAR",
      "dbLength": 36,
      "dbPointLength": 0,
      "dbDefaultVal": "",
      "dbIsKey": 1,
      "dbIsNull": 0,
      "fieldShowType": "text",
      "fieldHref": "",
      "fieldLength": 36,
      "fieldValidType": "",
      "fieldMustInput": "1",
      "fieldExtendJson": "",
      "fieldDefaultValue": "",
      "isReadOnly": 0,
      "isListShow": 0,
      "isFormShow": 0,
      "isQueryMode": 0,
      "dictField": "",
      "dictTable": "",
      "dictText": "",
      "orderNum": 1
    },
    {
      "dbFieldName": "employee_no",
      "dbFieldTxt": "工号",
      "dbType": "VARCHAR",
      "dbLength": 20,
      "dbPointLength": 0,
      "dbDefaultVal": "",
      "dbIsKey": 0,
      "dbIsNull": 0,
      "fieldShowType": "text",
      "fieldHref": "",
      "fieldLength": 20,
      "fieldValidType": "",
      "fieldMustInput": "1",
      "fieldExtendJson": "",
      "fieldDefaultValue": "",
      "isReadOnly": 0,
      "isListShow": 1,
      "isFormShow": 1,
      "isQueryMode": 1,
      "dictField": "",
      "dictTable": "",
      "dictText": "",
      "orderNum": 8
    },
    {
      "dbFieldName": "name",
      "dbFieldTxt": "姓名",
      "dbType": "VARCHAR",
      "dbLength": 50,
      "dbPointLength": 0,
      "dbDefaultVal": "",
      "dbIsKey": 0,
      "dbIsNull": 0,
      "fieldShowType": "text",
      "fieldHref": "",
      "fieldLength": 50,
      "fieldValidType": "",
      "fieldMustInput": "1",
      "fieldExtendJson": "",
      "fieldDefaultValue": "",
      "isReadOnly": 0,
      "isListShow": 1,
      "isFormShow": 1,
      "isQueryMode": 1,
      "dictField": "",
      "dictTable": "",
      "dictText": "",
      "orderNum": 9
    }
  ]
}
```
