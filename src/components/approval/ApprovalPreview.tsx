'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  CheckCircle2,
  XCircle,
  Edit3,
  User,
  Copy,
} from 'lucide-react';
import type { ApprovalRequest } from '@/lib/types/approval';
import { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';

interface ApprovalPreviewProps {
  approval: ApprovalRequest;
  onApprove?: () => void;
  onReject?: () => void;
  onModify?: (content: string) => void;
  onTakeover?: () => void;
  className?: string;
}

export function ApprovalPreview({
  approval,
  onApprove,
  onReject,
  onModify,
  onTakeover,
  className,
}: ApprovalPreviewProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [modifiedContent, setModifiedContent] = useState(approval.preview.content);

  const handleCopy = () => {
    navigator.clipboard.writeText(approval.preview.content);
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="text-lg">审批预览</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <h4 className="text-sm font-medium">为什么需要审批</h4>
            <p className="text-sm text-muted-foreground">{approval.reasonDescription}</p>
          </div>
          <div className="space-y-2">
            <h4 className="text-sm font-medium">收件人信息</h4>
            <p className="text-sm">{approval.preview.recipient}</p>
            <p className="text-sm text-muted-foreground">{approval.preview.channel}</p>
          </div>
        </div>

        <Separator />

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium">对外预览</h4>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={handleCopy}>
                <Copy className="h-4 w-4 mr-2" />
                复制
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setIsEditing(!isEditing)}>
                <Edit3 className="h-4 w-4 mr-2" />
                {isEditing ? '取消编辑' : '编辑'}
              </Button>
            </div>
          </div>

          {isEditing ? (
            <Textarea
              value={modifiedContent}
              onChange={(e) => setModifiedContent(e.target.value)}
              rows={8}
              className="font-mono text-sm"
            />
          ) : (
            <div className="rounded-lg bg-muted/50 p-4 whitespace-pre-wrap text-sm">
              {approval.preview.content}
            </div>
          )}
        </div>

        {(approval.triggeringRule || approval.riskReason) && (
          <>
            <Separator />
            <div className="space-y-2">
              <h4 className="text-sm font-medium">触发规则与风险</h4>
              {approval.triggeringRule && (
                <p className="text-sm text-muted-foreground">
                  触发规则：{approval.triggeringRule}
                </p>
              )}
              {approval.riskReason && (
                <p className="text-sm text-red-600">风险原因：{approval.riskReason}</p>
              )}
            </div>
          </>
        )}

        <div className="flex gap-2 pt-2">
          <Button onClick={onApprove} className="gap-2">
            <CheckCircle2 className="h-4 w-4" />
            批准
          </Button>
          {isEditing && (
            <Button
              variant="secondary"
              className="gap-2"
              onClick={() => onModify?.(modifiedContent)}
            >
              <Edit3 className="h-4 w-4" />
              修改并发送
            </Button>
          )}
          <Button variant="outline" className="gap-2" onClick={onTakeover}>
            <User className="h-4 w-4" />
            接管
          </Button>
          <Button variant="ghost" className="gap-2 text-destructive" onClick={onReject}>
            <XCircle className="h-4 w-4" />
            拒绝
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
