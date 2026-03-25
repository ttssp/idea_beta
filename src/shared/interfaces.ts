/**
 * 与E1/E2/E3共享的接口
 */

// 占位文件 - 实际接口将与其他工程师共同定义
export interface SharedThreadContext {
  threadId: string;
  objective: string;
  status: string;
}

export interface SharedActionResult {
  success: boolean;
  actionId: string;
  timestamp: string;
}
