'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { mockApprovals, mockThreads } from '@/mocks';
import {
  CheckCircle2,
  XCircle,
  Edit3,
  User,
  Clock,
  ShieldAlert,
} from 'lucide-react';
import {
  APPROVAL_REQUEST_TYPE_LABELS,
  APPROVAL_STATUS_LABELS,
} from '@/lib/types/approval';
import { formatRelativeTime, truncateText } from '@/lib/utils';
import Link from 'next/link';

export default function ApprovalsPage() {
  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Approval Center</h1>
        <p className="text-muted-foreground mt-1">审批代理的动作请求</p>
      </div>

      <div className="space-y-4">
        {mockApprovals.map((approval) => {
          const thread = mockThreads.find((t) => t.id === approval.threadId);

          return (
            <Card key={approval.id} className="overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <CardTitle className="text-base">
                        {APPROVAL_REQUEST_TYPE_LABELS[approval.requestType]}
                      </CardTitle>
                      <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200">
                        {APPROVAL_STATUS_LABELS[approval.status]}
                      </Badge>
                    </div>
                    {thread && (
                      <p className="text-sm text-muted-foreground">
                        线程：<Link href={`/threads/${thread.id}`} className="hover:underline">{thread.title}</Link>
                      </p>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatRelativeTime(approval.createdAt)}
                  </span>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium flex items-center gap-2">
                      <ShieldAlert className="h-4 w-4 text-amber-500" />
                      为什么需要审批
                    </h4>
                    <p className="text-sm text-muted-foreground">{approval.reasonDescription}</p>
                    {approval.triggeringRule && (
                      <Badge variant="outline" className="text-xs">
                        规则：{approval.triggeringRule}
                      </Badge>
                    )}
                    {approval.riskReason && (
                      <p className="text-xs text-red-600">风险原因：{approval.riskReason}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium flex items-center gap-2">
                      <User className="h-4 w-4" />
                      对外预览
                    </h4>
                    <div className="rounded-lg bg-muted p-3">
                      <p className="text-xs text-muted-foreground mb-1">
                        收件人：{approval.preview.recipient}
                      </p>
                      <p className="text-xs text-muted-foreground mb-2">
                        渠道：{approval.preview.channel}
                      </p>
                      <p className="text-sm">{truncateText(approval.preview.content, 180)}</p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <Button className="gap-2">
                    <CheckCircle2 className="h-4 w-4" />
                    批准
                  </Button>
                  <Button variant="secondary" className="gap-2">
                    <Edit3 className="h-4 w-4" />
                    修改
                  </Button>
                  <Button variant="outline" className="gap-2">
                    <User className="h-4 w-4" />
                    接管
                  </Button>
                  <Button variant="ghost" className="gap-2 text-destructive">
                    <XCircle className="h-4 w-4" />
                    拒绝
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
        {mockApprovals.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">暂无待审批项</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
