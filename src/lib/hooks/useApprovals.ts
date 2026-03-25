'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { approvalsApi } from '@/lib/api';
import type { ApprovalRequest, ApprovalResolution } from '@/lib/types/approval';

export function useApprovals() {
  return useQuery({
    queryKey: ['approvals'],
    queryFn: approvalsApi.getApprovals,
  });
}

export function useApproval(id: string | null) {
  return useQuery({
    queryKey: ['approval', id],
    queryFn: () => (id ? approvalsApi.getApproval(id) : undefined),
    enabled: !!id,
  });
}

export function useResolveApproval() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, resolution }: { id: string; resolution: ApprovalResolution }) =>
      approvalsApi.resolveApproval(id, resolution),
    onSuccess: (updatedApproval) => {
      queryClient.setQueryData(['approval', updatedApproval.id], updatedApproval);
      queryClient.setQueryData(['approvals'], (old: ApprovalRequest[] = []) =>
        old.map((a) => (a.id === updatedApproval.id ? updatedApproval : a))
      );
    },
  });
}
