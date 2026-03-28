'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ArrowLeft, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  DELEGATION_PROFILE_LABELS,
  DELEGATION_PROFILE_DESCRIPTIONS,
  type DelegationProfile,
} from '@/lib/types/thread';
import { useCreateThread } from '@/lib/hooks/useThread';
import { useToast } from '@/lib/hooks/useToast';

export default function NewThreadPage() {
  const router = useRouter();
  const { toast } = useToast();
  const createThread = useCreateThread();

  const [formData, setFormData] = useState({
    title: '',
    objective: '',
    delegation: 'draft_first' as DelegationProfile,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title.trim()) {
      toast({
        title: '标题不能为空',
        description: '请输入线程标题',
        variant: 'destructive',
      });
      return;
    }

    try {
      const newThread = await createThread.mutateAsync({
        title: formData.title,
        objective: formData.objective,
        delegationProfile: formData.delegation,
      });

      toast({
        title: '线程创建成功',
        description: '新线程已创建，正在跳转...',
      });

      // 跳转到新创建的线程页面
      setTimeout(() => {
        router.push(`/threads/${newThread.id}`);
      }, 500);
    } catch (error) {
      toast({
        title: '创建失败',
        description: error instanceof Error ? error.message : '请重试',
        variant: 'destructive',
      });
    }
  };

  const isCreating = createThread.isPending;

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="mb-6">
        <Button variant="ghost" size="sm" asChild className="mb-4">
          <Link href="/">
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回
          </Link>
        </Button>
        <h1 className="text-2xl font-bold">新建线程</h1>
        <p className="text-muted-foreground mt-1">创建一个新的通信线程</p>
      </div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>线程信息</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title">标题 *</Label>
              <Input
                id="title"
                placeholder="简明描述这个线程的目标"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                disabled={isCreating}
                autoFocus
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="objective">目标</Label>
              <Textarea
                id="objective"
                placeholder="详细描述你想达成的目标..."
                rows={4}
                value={formData.objective}
                onChange={(e) => setFormData({ ...formData, objective: e.target.value })}
                disabled={isCreating}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="participants">参与者</Label>
              <Input id="participants" placeholder="添加参与者（开发中）" disabled />
            </div>

            <div className="space-y-2">
              <Label htmlFor="delegation">委托档位</Label>
              <Select
                defaultValue={formData.delegation}
                onValueChange={(value) =>
                  setFormData({ ...formData, delegation: value as DelegationProfile })
                }
                disabled={isCreating}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(DELEGATION_PROFILE_LABELS).map(([key, label]) => (
                    <SelectItem key={key} value={key}>
                      <div className="flex flex-col items-start">
                        <span>{label}</span>
                        <span className="text-xs text-muted-foreground">
                          {DELEGATION_PROFILE_DESCRIPTIONS[key as keyof typeof DELEGATION_PROFILE_DESCRIPTIONS]}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="submit" className="flex-1" disabled={isCreating}>
                {isCreating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    创建中...
                  </>
                ) : (
                  '创建线程'
                )}
              </Button>
              <Button type="button" variant="outline" asChild disabled={isCreating}>
                <Link href="/">取消</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
}

