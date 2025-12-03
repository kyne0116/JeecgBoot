/**
 * 软著对话系统 - Pinia状态管理
 *
 * @author Claude Code
 * @since 2025-12-03 (T017)
 */

import { defineStore } from 'pinia';
import { store } from '/@/store';
import type { CopyrightSession, CopyrightMessage, CopyrightFile } from '/@/api/model/copyrightModel';

interface CopyrightState {
  // 当前会话
  currentSession: CopyrightSession | null;

  // 会话列表
  sessionList: CopyrightSession[];

  // 当前会话的消息列表
  messageList: CopyrightMessage[];

  // 当前会话的文件列表
  fileList: CopyrightFile[];

  // SSE连接状态
  sseConnected: boolean;

  // 加载状态
  loading: boolean;
}

export const useCopyrightStore = defineStore({
  id: 'app-copyright',
  state: (): CopyrightState => ({
    currentSession: null,
    sessionList: [],
    messageList: [],
    fileList: [],
    sseConnected: false,
    loading: false,
  }),

  getters: {
    /**
     * 获取当前会话ID
     */
    getCurrentSessionId(): string | null {
      return this.currentSession?.sessionId || null;
    },

    /**
     * 获取当前会话状态
     */
    getCurrentSessionStatus(): string | null {
      return this.currentSession?.sessionStatus || null;
    },

    /**
     * 是否正在澄清中
     */
    isClarifying(): boolean {
      return this.currentSession?.sessionStatus === 'CLARIFYING';
    },

    /**
     * 是否正在生成中
     */
    isGenerating(): boolean {
      return this.currentSession?.sessionStatus === 'GENERATING';
    },

    /**
     * 是否已完成
     */
    isCompleted(): boolean {
      return this.currentSession?.sessionStatus === 'COMPLETED';
    },

    /**
     * 获取消息数量
     */
    getMessageCount(): number {
      return this.messageList.length;
    },

    /**
     * 获取文件数量
     */
    getFileCount(): number {
      return this.fileList.length;
    },
  },

  actions: {
    /**
     * 设置当前会话
     */
    setCurrentSession(session: CopyrightSession | null) {
      this.currentSession = session;
    },

    /**
     * 更新当前会话状态
     */
    updateSessionStatus(status: string) {
      if (this.currentSession) {
        this.currentSession.sessionStatus = status as any;
      }
    },

    /**
     * 设置会话列表
     */
    setSessionList(list: CopyrightSession[]) {
      this.sessionList = list;
    },

    /**
     * 添加会话到列表
     */
    addSession(session: CopyrightSession) {
      this.sessionList.unshift(session);
    },

    /**
     * 设置消息列表
     */
    setMessageList(messages: CopyrightMessage[]) {
      this.messageList = messages;
    },

    /**
     * 添加消息
     */
    addMessage(message: CopyrightMessage) {
      this.messageList.push(message);
    },

    /**
     * 清空消息列表
     */
    clearMessageList() {
      this.messageList = [];
    },

    /**
     * 设置文件列表
     */
    setFileList(files: CopyrightFile[]) {
      this.fileList = files;
    },

    /**
     * 添加文件
     */
    addFile(file: CopyrightFile) {
      this.fileList.push(file);
    },

    /**
     * 清空文件列表
     */
    clearFileList() {
      this.fileList = [];
    },

    /**
     * 设置SSE连接状态
     */
    setSSEConnected(connected: boolean) {
      this.sseConnected = connected;
    },

    /**
     * 设置加载状态
     */
    setLoading(loading: boolean) {
      this.loading = loading;
    },

    /**
     * 重置状态
     */
    resetState() {
      this.currentSession = null;
      this.messageList = [];
      this.fileList = [];
      this.sseConnected = false;
      this.loading = false;
    },

    /**
     * 切换会话
     */
    switchSession(session: CopyrightSession) {
      this.setCurrentSession(session);
      this.clearMessageList();
      this.clearFileList();
      this.setSSEConnected(false);
    },
  },
});

// 在setup外使用
export function useCopyrightStoreWithOut() {
  return useCopyrightStore(store);
}
