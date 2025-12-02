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
    title: '会话ID',
    align:"center",
    dataIndex: 'sessionId'
   },
   {
    title: 'Agent名称',
    align:"center",
    dataIndex: 'agentName'
   },
   {
    title: 'Agent类型',
    align:"center",
    dataIndex: 'agentType'
   },
   {
    title: '执行阶段',
    align:"center",
    dataIndex: 'executionPhase'
   },
   {
    title: '执行状态',
    align:"center",
    dataIndex: 'status_dictText'
   },
   {
    title: '开始时间',
    align:"center",
    dataIndex: 'startTime'
   },
   {
    title: '结束时间',
    align:"center",
    dataIndex: 'endTime'
   },
   {
    title: '执行时长(毫秒)',
    align:"center",
    dataIndex: 'durationMs'
   },
   {
    title: '重试次数',
    align:"center",
    dataIndex: 'retryCount'
   },
   {
    title: '使用的模型名称',
    align:"center",
    dataIndex: 'modelName'
   },
   {
    title: '总Token消耗',
    align:"center",
    dataIndex: 'totalTokens'
   },
   {
    title: 'Prompt Token数',
    align:"center",
    dataIndex: 'promptTokens'
   },
   {
    title: '完成Token数',
    align:"center",
    dataIndex: 'completionTokens'
   },
];
//查询数据
export const searchFormSchema: FormSchema[] = [
	{
      label: "会话ID",
      field: 'sessionId',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "Agent名称",
      field: 'agentName',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "Agent类型",
      field: 'agentType',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "执行阶段",
      field: 'executionPhase',
      component: 'Input',
      //colProps: {span: 6},
 	},
	{
      label: "执行状态",
      field: 'status',
      component: 'JSelectMultiple',
      componentProps:{
          dictCode:"status"
      },
      //colProps: {span: 6},
 	},
     {
      label: "开始时间",
      field: "startTime",
      component: 'RangePicker',
      componentProps: {
          valueType: 'Date',
          showTime:true
      },
      //colProps: {span: 6},
	},
     {
      label: "结束时间",
      field: "endTime",
      component: 'RangePicker',
      componentProps: {
          valueType: 'Date',
          showTime:true
      },
      //colProps: {span: 6},
	},
	{
      label: "使用的模型名称",
      field: 'modelName',
      component: 'Input',
      //colProps: {span: 6},
 	},
];
//表单数据
export const formSchema: FormSchema[] = [
  {
    label: '会话ID',
    field: 'sessionId',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入会话ID!'},
          ];
     },
  },
  {
    label: 'Agent名称',
    field: 'agentName',
    component: 'Input',
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入Agent名称!'},
          ];
     },
  },
  {
    label: 'Agent类型',
    field: 'agentType',
    component: 'Input',
  },
  {
    label: '执行阶段',
    field: 'executionPhase',
    component: 'Input',
  },
  {
    label: '执行状态',
    field: 'status',
    component: 'JDictSelectTag',
    componentProps:{
        dictCode:"status"
     },
    dynamicRules: ({model,schema}) => {
          return [
                 { required: true, message: '请输入执行状态!'},
          ];
     },
  },
  {
    label: '开始时间',
    field: 'startTime',
    component: 'DatePicker',
    componentProps: {
       showTime: true,
       valueFormat: 'YYYY-MM-DD HH:mm:ss'
     },
  },
  {
    label: '结束时间',
    field: 'endTime',
    component: 'DatePicker',
    componentProps: {
       showTime: true,
       valueFormat: 'YYYY-MM-DD HH:mm:ss'
     },
  },
  {
    label: '执行时长(毫秒)',
    field: 'durationMs',
    component: 'InputNumber',
  },
  {
    label: '输入参数JSON',
    field: 'inputParams',
    component: 'InputTextArea',
  },
  {
    label: '输出结果JSON',
    field: 'outputResult',
    component: 'InputTextArea',
  },
  {
    label: '错误信息',
    field: 'errorMessage',
    component: 'InputTextArea',
  },
  {
    label: '错误堆栈',
    field: 'errorStack',
    component: 'InputTextArea',
  },
  {
    label: '重试次数',
    field: 'retryCount',
    defaultValue: 0,
    component: 'InputNumber',
  },
  {
    label: '使用的模型名称',
    field: 'modelName',
    component: 'Input',
  },
  {
    label: '总Token消耗',
    field: 'totalTokens',
    component: 'InputNumber',
  },
  {
    label: 'Prompt Token数',
    field: 'promptTokens',
    component: 'InputNumber',
  },
  {
    label: '完成Token数',
    field: 'completionTokens',
    component: 'InputNumber',
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
  sessionId: {title: '会话ID',order: 1,view: 'text', type: 'string',},
  agentName: {title: 'Agent名称',order: 2,view: 'text', type: 'string',},
  agentType: {title: 'Agent类型',order: 3,view: 'text', type: 'string',},
  executionPhase: {title: '执行阶段',order: 4,view: 'text', type: 'string',},
  status: {title: '执行状态',order: 5,view: 'number', type: 'number',dictCode: 'status',},
  startTime: {title: '开始时间',order: 6,view: 'datetime', type: 'string',},
  endTime: {title: '结束时间',order: 7,view: 'datetime', type: 'string',},
  durationMs: {title: '执行时长(毫秒)',order: 8,view: 'number', type: 'number',},
  retryCount: {title: '重试次数',order: 13,view: 'number', type: 'number',},
  modelName: {title: '使用的模型名称',order: 14,view: 'text', type: 'string',},
  totalTokens: {title: '总Token消耗',order: 15,view: 'number', type: 'number',},
  promptTokens: {title: 'Prompt Token数',order: 16,view: 'number', type: 'number',},
  completionTokens: {title: '完成Token数',order: 17,view: 'number', type: 'number',},
};

/**
* 流程表单调用这个方法获取formSchema
* @param param
*/
export function getBpmFormSchema(_formData): FormSchema[]{
  // 默认和原始表单保持一致 如果流程中配置了权限数据，这里需要单独处理formSchema
  return formSchema;
}