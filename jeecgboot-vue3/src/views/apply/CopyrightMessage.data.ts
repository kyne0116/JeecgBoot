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
    title: '对话ID',
    align:"center",
    dataIndex: 'sessionId'
   },
   {
    title: '消息序号',
    align:"center",
    dataIndex: 'sequenceNo'
   },
   {
    title: '角色',
    align:"center",
    dataIndex: 'role'
   },
   {
    title: '消息类型',
    align:"center",
    dataIndex: 'messageType'
   },
   {
    title: 'Agent名称',
    align:"center",
    dataIndex: 'agentName'
   },
];
//查询数据
export const searchFormSchema: FormSchema[] = [
	{
      label: "对话ID",
      field: 'sessionId',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "角色",
      field: 'role',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "消息类型",
      field: 'messageType',
      component: 'Input',
      //colProps: {span: 6},
 	},
];
//表单数据
export const formSchema: FormSchema[] = [
  {
    label: '对话ID',
    field: 'sessionId',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入对话ID!'},
          ];
     },
  },
  {
    label: '消息序号',
    field: 'sequenceNo',
    component: 'InputNumber',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入消息序号!'},
          ];
     },
  },
  {
    label: '角色',
    field: 'role',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入角色!'},
          ];
     },
  },
  {
    label: '消息内容',
    field: 'content',
    component: 'InputTextArea',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入消息内容!'},
          ];
     },
  },
  {
    label: '消息类型',
    field: 'messageType',
    defaultValue: "text",
    component: 'Input',
  },
  {
    label: 'Agent名称',
    field: 'agentName',
    component: 'Input',
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
  sessionId: {title: '对话ID',order: 1,view: 'text', type: 'string',},
  sequenceNo: {title: '消息序号',order: 2,view: 'number', type: 'number',},
  role: {title: '角色',order: 3,view: 'text', type: 'string',},
  messageType: {title: '消息类型',order: 5,view: 'text', type: 'string',},
  agentName: {title: 'Agent名称',order: 6,view: 'text', type: 'string',},
};

/**
* 流程表单调用这个方法获取formSchema
* @param param
*/
export function getBpmFormSchema(_formData): FormSchema[]{
  // 默认和原始表单保持一致 如果流程中配置了权限数据，这里需要单独处理formSchema
  return formSchema;
}