/**
 * 软著对话系统 - API接口
 *
 * @author Claude Code
 * @since 2025-12-03 (T017)
 */

import { defHttp } from '/@/utils/http/axios';
import { useGlobSetting } from '/@/hooks/setting';
import type {
  CopyrightSession,
  CopyrightMessage,
  CopyrightFile,
  CreateSessionParams,
  SendMessageParams,
  SessionListParams,
  PageResult,
} from './model/copyrightModel';

const globSetting = useGlobSetting();

enum Api {
  // Session APIs
  CREATE_SESSION = '/jeecg-boot/copyright/sse/session/create',
  GET_SESSION = '/jeecg-boot/copyright/sse/session',
  SESSION_LIST = '/jeecg-boot/apply/copyrightSession/list',

  // Message APIs
  SEND_MESSAGE = '/jeecg-boot/copyright/sse/user-input',

  // File APIs
  SESSION_FILES = '/jeecg-boot/apply/copyrightFile/session',
  DOWNLOAD_FILE = '/jeecg-boot/apply/copyrightFile/download',
  DOWNLOAD_ALL = '/jeecg-boot/apply/copyrightFile/download-all',

  // SSE连接
  SSE_CONNECT = '/jeecg-boot/copyright/sse/connect',
}

/**
 * 创建新会话
 */
export const createSession = (params: CreateSessionParams) =>
  defHttp.post<CopyrightSession>({ url: Api.CREATE_SESSION, params });

/**
 * 获取会话详情
 */
export const getSession = (sessionId: string) =>
  defHttp.get<CopyrightSession>({ url: `${Api.GET_SESSION}/${sessionId}` });

/**
 * 获取会话列表
 */
export const getSessionList = (params: SessionListParams) =>
  defHttp.get<PageResult<CopyrightSession>>({ url: Api.SESSION_LIST, params });

/**
 * 发送用户消息
 */
export const sendMessage = (params: SendMessageParams) =>
  defHttp.post<void>({ url: Api.SEND_MESSAGE, params });

/**
 * 获取会话文件列表
 */
export const getSessionFiles = (sessionId: string) =>
  defHttp.get<CopyrightFile[]>({ url: `${Api.SESSION_FILES}/${sessionId}` });

/**
 * 构建SSE连接URL
 */
export const buildSSEUrl = (sessionId: string): string => {
  const baseUrl = globSetting.domainUrl;
  return `${baseUrl}${Api.SSE_CONNECT}/${sessionId}`;
};

/**
 * 构建文件下载URL
 */
export const buildFileDownloadUrl = (fileId: string): string => {
  const baseUrl = globSetting.domainUrl;
  return `${baseUrl}${Api.DOWNLOAD_FILE}/${fileId}`;
};

/**
 * 构建批量下载URL
 */
export const buildDownloadAllUrl = (sessionId: string): string => {
  const baseUrl = globSetting.domainUrl;
  return `${baseUrl}${Api.DOWNLOAD_ALL}/${sessionId}`;
};
