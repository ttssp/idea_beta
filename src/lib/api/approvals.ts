import type { ApprovalRequest, ApprovalResolution } from '@/lib/types/approval';
import { mockApprovals } from '@/mocks';
import { USE_MOCK_API } from '@/lib/utils/constants';

const mockApi = {
  getApprovals: async (): Promise<ApprovalRequest[]> => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return mockApprovals;
  },

  getApproval: async (id: string): Promise<ApprovalRequest | undefined> => {
    await new Promise((resolve) => setTimeout(resolve, 200));
    return mockApprovals.find((a) => a.id === id);
  },

  resolveApproval: async (
    id: string,
    resolution: ApprovalResolution
  ): Promise<ApprovalRequest> => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    const approval = mockApprovals.find((a) => a.id === id);
    if (!approval) throw new Error('Approval not found');
    return {
      ...approval,
      status: resolution.status,
      resolvedAt: new Date().toISOString(),
    };
  },
};

const realApi = {
  getApprovals: async (): Promise<ApprovalRequest[]> => {
    throw new Error('Not implemented');
  },
  getApproval: async (_id: string): Promise<ApprovalRequest> => {
    throw new Error('Not implemented');
  },
  resolveApproval: async (
    _id: string,
    _resolution: ApprovalResolution
  ): Promise<ApprovalRequest> => {
    throw new Error('Not implemented');
  },
};

export const approvalsApi = USE_MOCK_API ? mockApi : realApi;
