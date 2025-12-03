/**
 * 软著对话系统 - 路由配置
 *
 * @author Claude Code
 * @since 2025-12-03 (T017)
 */

import type { AppRouteModule } from '/@/router/types';
import { LAYOUT } from '/@/router/constant';

const copyright: AppRouteModule = {
  path: '/copyright',
  name: 'Copyright',
  component: LAYOUT,
  redirect: '/copyright/chat',
  meta: {
    orderNo: 100,
    icon: 'ant-design:copyright-outlined',
    title: '软著申报',
  },
  children: [
    {
      path: 'chat',
      name: 'CopyrightChat',
      component: () => import('/@/views/copyright/CopyrightChatApp.vue'),
      meta: {
        title: '智能对话',
        icon: 'ant-design:message-outlined',
      },
    },
    {
      path: 'records',
      name: 'CopyrightRecords',
      component: () => import('/@/views/copyright/CopyrightRecordList.vue'),
      meta: {
        title: '申报记录',
        icon: 'ant-design:file-text-outlined',
      },
    },
  ],
};

export default copyright;
