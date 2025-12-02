import {BasicColumn} from '/@/components/Table';
import {FormSchema} from '/@/components/Table';
import { rules} from '/@/utils/helper/validator';
import { render } from '/@/utils/common/renderUtils';
import { getWeekMonthQuarterYear } from '/@/utils';
//列表数据
export const columns: BasicColumn[] = [
   {
    title: '更新时间',
    align:"center",
    dataIndex: 'updateTime'
   },
   {
    title: '配置键',
    align:"center",
    dataIndex: 'configKey'
   },
   {
    title: '配置类型',
    align:"center",
    dataIndex: 'configType'
   },
   {
    title: '配置分组',
    align:"center",
    dataIndex: 'configGroup'
   },
   {
    title: '配置描述',
    align:"center",
    dataIndex: 'description'
   },
   {
    title: '是否系统配置',
    align:"center",
    dataIndex: 'isSystem_dictText'
   },
   {
    title: '是否加密存储',
    align:"center",
    dataIndex: 'isEncrypted_dictText'
   },
   {
    title: '排序顺序',
    align:"center",
    sorter: true,
    dataIndex: 'sortOrder'
   },
   {
    title: '状态',
    align:"center",
    dataIndex: 'status_dictText'
   },
];
//查询数据
export const searchFormSchema: FormSchema[] = [
	{
      label: "配置键",
      field: 'configKey',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "配置类型",
      field: 'configType',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "配置分组",
      field: 'configGroup',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "是否系统配置",
      field: 'isSystem',
      component: 'JSelectMultiple',
      componentProps:{
          dictCode:"yn"
      },
      //colProps: {span: 6},
 	},
	{
      label: "是否加密存储",
      field: 'isEncrypted',
      component: 'JSelectMultiple',
      componentProps:{
          dictCode:"yn"
      },
      //colProps: {span: 6},
 	},
	{
      label: "状态",
      field: 'status',
      component: 'JSelectMultiple',
      componentProps:{
          dictCode:"status"
      },
      //colProps: {span: 6},
 	},
];
//表单数据
export const formSchema: FormSchema[] = [
  {
    label: '配置键',
    field: 'configKey',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入配置键!'},
          ];
     },
  },
  {
    label: '配置值',
    field: 'configValue',
    component: 'InputTextArea',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入配置值!'},
          ];
     },
  },
  {
    label: '配置类型',
    field: 'configType',
    defaultValue: "string",
    component: 'Input',
  },
  {
    label: '配置分组',
    field: 'configGroup',
    defaultValue: "system",
    component: 'Input',
  },
  {
    label: '配置描述',
    field: 'description',
    component: 'InputTextArea',
  },
  {
    label: '是否系统配置',
    field: 'isSystem',
    defaultValue: 0,
    component: 'JDictSelectTag',
    componentProps:{
        dictCode:"yn"
     },
  },
  {
    label: '是否加密存储',
    field: 'isEncrypted',
    defaultValue: 0,
    component: 'JDictSelectTag',
    componentProps:{
        dictCode:"yn"
     },
  },
  {
    label: '排序顺序',
    field: 'sortOrder',
    defaultValue: 0,
    component: 'InputNumber',
  },
  {
    label: '状态',
    field: 'status',
    defaultValue: 1,
    component: 'JDictSelectTag',
    componentProps:{
        dictCode:"status"
     },
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入状态!'},
          ];
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
  configKey: {title: '配置键',order: 1,view: 'text', type: 'string',},
  configType: {title: '配置类型',order: 3,view: 'text', type: 'string',},
  configGroup: {title: '配置分组',order: 4,view: 'text', type: 'string',},
  description: {title: '配置描述',order: 5,view: 'textarea', type: 'string',},
  isSystem: {title: '是否系统配置',order: 6,view: 'number', type: 'number',dictCode: 'yn',},
  isEncrypted: {title: '是否加密存储',order: 7,view: 'number', type: 'number',dictCode: 'yn',},
  sortOrder: {title: '排序顺序',order: 8,view: 'number', type: 'number',},
  status: {title: '状态',order: 9,view: 'number', type: 'number',dictCode: 'status',},
};

/**
* 流程表单调用这个方法获取formSchema
* @param param
*/
export function getBpmFormSchema(_formData): FormSchema[]{
  // 默认和原始表单保持一致 如果流程中配置了权限数据，这里需要单独处理formSchema
  return formSchema;
}