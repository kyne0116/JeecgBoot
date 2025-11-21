import {BasicColumn} from '/@/components/Table';
import {FormSchema} from '/@/components/Table';
import { rules} from '/@/utils/helper/validator';
import { render } from '/@/utils/common/renderUtils';
import { getWeekMonthQuarterYear } from '/@/utils';
//列表数据
export const columns: BasicColumn[] = [
   {
    title: '组织名称',
    align:"center",
    dataIndex: 'orgname'
   },
   {
    title: '显示名称',
    align:"center",
    dataIndex: 'displayName'
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
    title: '变更前组织名称',
    align:"center",
    dataIndex: 'preOrgname'
   },
   {
    title: '组织代码',
    align:"center",
    dataIndex: 'orgcode'
   },
   {
    title: '组织类型',
    align:"center",
    dataIndex: 'orgtype'
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
      label: "变更前组织名称",
      field: 'preOrgname',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "组织名称",
      field: 'orgname',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "组织代码",
      field: 'orgcode',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "组织类型",
      field: 'orgtype',
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
      field: "syncDate",
      component: 'RangePicker',
      componentProps: {
        valueType: 'Date',
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
    label: '变更前组织名称',
    field: 'preOrgname',
    component: 'Input',
  },
  {
    label: '组织名称',
    field: 'orgname',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入组织名称!'},
          ];
     },
  },
  {
    label: '组织代码',
    field: 'orgcode',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入组织代码!'},
          ];
     },
  },
  {
    label: '20位组织代码',
    field: 'orgcode20',
    component: 'Input',
  },
  {
    label: '组织类型',
    field: 'orgtype',
    component: 'Input',
  },
  {
    label: '上级组织名称',
    field: 'parentOrgname',
    component: 'Input',
  },
  {
    label: '上级组织代码',
    field: 'parentOrgcode',
    component: 'Input',
  },
  {
    label: '上级20位组织代码',
    field: 'parentOrgcode20',
    component: 'Input',
  },
  {
    label: '显示名称',
    field: 'displayName',
    component: 'Input',
  },
  {
    label: '显示顺序',
    field: 'displayOrder',
    component: 'InputNumber',
  },
  {
    label: '层级字典值',
    field: 'levelDictValue',
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
  preOrgname: {title: '变更前组织名称',order: 2,view: 'text', type: 'string',},
  orgname: {title: '组织名称',order: 3,view: 'text', type: 'string',},
  orgcode: {title: '组织代码',order: 4,view: 'text', type: 'string',},
  orgtype: {title: '组织类型',order: 6,view: 'text', type: 'string',},
  displayName: {title: '显示名称',order: 10,view: 'text', type: 'string',},
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