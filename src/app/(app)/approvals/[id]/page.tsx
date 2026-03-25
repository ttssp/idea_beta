'use client';

import { notFound } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { ApprovalPreview } from '@/components/approval';
import { mockApprovals } from '@/mocks';

interface ApprovalDetailPageProps {
  params: { id: string };
}

export default function ApprovalDetailPage({ params }: ApprovalDetailPageProps) {
  const approval = mockApprovals.find((a) => a.id === params.id);

  if (!approval) {
    notFound();
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <div className="mb-6">
        <Button variant="ghost" size="sm" asChild className="mb-4">
          <Link href="/approvals">
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回审批中心
          </Link>
        </Button>
      </div>

      <ApprovalPreview
        approval={approval}
        onApprove={() => console.log('Approved')}
        onReject={() => console.log('Rejected')}
        onModify={(content) => console.log('Modified:', content)}
        onTakeover={() => console.log('Takeover')}
      />
    </div>
  );
}
