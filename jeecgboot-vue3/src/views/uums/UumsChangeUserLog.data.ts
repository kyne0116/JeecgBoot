import {BasicColumn} from '/@/components/Table';
import {FormSchema} from '/@/components/Table';
import { rules} from '/@/utils/helper/validator';
import { render } from '/@/utils/common/renderUtils';
import { getWeekMonthQuarterYear } from '/@/utils';
//列表数据
export const columns: BasicColumn[] = [
   {
    title: '用户名',
    align:"center",
    dataIndex: 'username'
   },
   {
    title: '真实姓名',
    align:"center",
    dataIndex: 'truename'
   },
   {
    title: '同步日期',
    align:"center",
    dataIndex: 'syncDate',
    customRender:({text}) =>{
      text = !text ? "" : (text.length > 10 ? text.substr(0,10) : text);
      return text;
    },
   },
   {
    title: '同步状态',
    align:"center",
    dataIndex: 'resultFlag_dictText'
   },
   {
    title: '处理结果',
    align:"center",
    dataIndex: 'result'
   },
   {
    title: '更新时间',
    align:"center",
    dataIndex: 'updateTime'
   },
   {
    title: '变更类型',
    align:"center",
    dataIndex: 'changeType'
   },
   {
    title: '显示顺序',
    align:"center",
    dataIndex: 'displayOrder'
   },
   {
    title: '员工编号',
    align:"center",
    dataIndex: 'employeeNumber'
   },
   {
    title: '职位名称',
    align:"center",
    dataIndex: 'positionName'
   },
   {
    title: '首选手机号',
    align:"center",
    dataIndex: 'preferredMobile'
   },
   {
    title: '邮箱',
    align:"center",
    dataIndex: 'email'
   },
];
//查询数据
export const searchFormSchema: FormSchema[] = [
	{
      label: "变更类型",
      field: 'changeType',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "用户名",
      field: 'username',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "当前组织编码20位",
      field: 'currentOrgCode20',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "员工编号",
      field: 'employeeNumber',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "职位名称",
      field: 'positionName',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "真实姓名",
      field: 'truename',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "变更前组织编码",
      field: 'preOrgcode',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "变更后组织编码",
      field: 'currentOrgcode',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "首选手机号",
      field: 'preferredMobile',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "邮箱",
      field: 'email',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "同步状态",
      field: 'resultFlag',
      component: 'JDictSelectTag',
      componentProps: {
        dictCode: 'success_fail',
        placeholder: '请选择同步状态',
      },
      //colProps: {span: 6},
 	},
	{
      label: "同步日期",
      field: 'syncDate',
      component: 'DatePicker',
      componentProps: {
        valueFormat: 'YYYY-MM-DD'
      },
      //colProps: {span: 6},
 	},
];
//表单数据
export const formSchema: FormSchema[] = [
  {
    label: '变更类型',
    field: 'changeType',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入变更类型!'},
          ];
     },
  },
  {
    label: '用户名',
    field: 'username',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入用户名!'},
          ];
     },
  },
  {
    label: '显示顺序',
    field: 'displayOrder',
    component: 'InputNumber',
  },
  {
    label: '当前组织编码20位',
    field: 'currentOrgCode20',
    component: 'Input',
  },
  {
    label: '员工编号',
    field: 'employeeNumber',
    component: 'Input',
  },
  {
    label: '职位名称',
    field: 'positionName',
    component: 'Input',
  },
  {
    label: '真实姓名',
    field: 'truename',
    component: 'Input',
  },
  {
    label: '变更前组织编码',
    field: 'preOrgcode',
    component: 'Input',
  },
  {
    label: '变更后组织编码',
    field: 'currentOrgcode',
    component: 'Input',
  },
  {
    label: '变更前职位名称',
    field: 'prePositionName',
    component: 'Input',
  },
  {
    label: '变更后职位名称',
    field: 'currentPositionName',
    component: 'Input',
  },
  {
    label: '首选手机号',
    field: 'preferredMobile',
    component: 'Input',
  },
  {
    label: '邮箱',
    field: 'email',
    component: 'Input',
  },
  {
    label: '处理结果',
    field: 'result',
    component: 'InputTextArea',
  },
  {
    label: '同步状态',
    field: 'resultFlag',
    component: 'JDictSelectTag',
    componentProps: {
      dictCode: 'success_fail',
      placeholder: '请选择同步状态',
    },
  },
  {
    label: '同步日期',
    field: 'syncDate',
    component: 'DatePicker',
    componentProps: {
      valueFormat: 'YYYY-MM-DD'
    },
  },
	// TODO 主键隐藏字段，目前写死为ID
	{
	  label: '',
	  field: 'id',
	  component: 'Input',
	  show: false
	},
];

// 高级查询数据
export const superQuerySchema = {
  updateTime: {title: '更新时间',order: 0,view: 'datetime', type: 'string',},
  changeType: {title: '变更类型',order: 1,view: 'text', type: 'string',},
  username: {title: '用户名',order: 2,view: 'text', type: 'string',},
  displayOrder: {title: '显示顺序',order: 3,view: 'number', type: 'number',},
  employeeNumber: {title: '员工编号',order: 5,view: 'text', type: 'string',},
  positionName: {title: '职位名称',order: 6,view: 'text', type: 'string',},
  truename: {title: '真实姓名',order: 7,view: 'text', type: 'string',},
  preferredMobile: {title: '首选手机号',order: 12,view: 'text', type: 'string',},
  email: {title: '邮箱',order: 13,view: 'text', type: 'string',},
  result: {title: '处理结果',order: 14,view: 'textarea', type: 'string',},
  resultFlag: {title: '同步状态',order: 15,view: 'text', type: 'string',},
  syncDate: {title: '同步日期',order: 16,view: 'date', type: 'string',},
};

/**
* 流程表单调用这个方法获取formSchema
* @param param
*/
export function getBpmFormSchema(_formData): FormSchema[]{
  // 默认和原始表单保持一致 如果流程中配置了权限数据，这里需要单独处理formSchema
  return formSchema;
}