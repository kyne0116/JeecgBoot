/**
 * 软著对话系统 - API数据模型
 *
 * @author Claude Code
 * @since 2025-12-03 (T017)
 */

/**
 * 会话信息
 */
export interface CopyrightSession {
  id: string;
  sessionId: string;
  sessionName?: string;
  userId?: string;
  username?: string;
  sessionStatus: 'WAITING' | 'CLARIFYING' | 'GENERATING' | 'COMPLETED' | 'ERROR';
  initialRequirement?: string;
  currentQuestion?: string;
  questionCount?: number;
  requirement?: string;
  createTime?: string;
  updateTime?: string;
}

/**
 * 会话消息
 */
export interface CopyrightMessage {
  id?: string;
  sessionId: string;
  messageType: 'USER' | 'AGENT' | 'SYSTEM';
  content: string;
  createTime?: string;
  metadata?: Record<string, any>;
}

/**
 * 文件记录
 */
export interface CopyrightFile {
  id: string;
  sessionId: string;
  fileType: 'source_code' | 'info_form' | 'desc_doc';
  filename: string;
  filePath: string;
  fileSize: number;
  fileCategory?: string;
  fileExtension?: string;
  mimeType?: string;
  qualityStatus?: 'pending' | 'passed' | 'failed' | 'checking';
  qualityScore?: number;
  qualityReportJson?: string;
  codeLines?: number;
  docWordCount?: number;
  createTime?: string;
  updateTime?: string;
}

/**
 * SSE事件数据
 */
export interface SSEEventData {
  type: 'QUESTION' | 'THINKING' | 'COMPLETED' | 'ERROR' | 'HEARTBEAT';
  data?: any;
  message?: string;
  sessionStatus?: string;
  timestamp?: number;
}

/**
 * 创建会话参数
 */
export interface CreateSessionParams {
  userId?: string;
  username?: string;
  initialRequirement: string;
}

/**
 * 发送消息参数
 */
export interface SendMessageParams {
  sessionId: string;
  userInput: string;
}

/**
 * 会话列表查询参数
 */
export interface SessionListParams {
  userId?: string;
  username?: string;
  pageNo?: number;
  pageSize?: number;
}

/**
 * 分页结果
 */
export interface PageResult<T> {
  records: T[];
  total: number;
  size: number;
  current: number;
  pages: number;
}
