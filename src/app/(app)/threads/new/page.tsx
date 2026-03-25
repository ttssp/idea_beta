'use client';

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
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import {
  DELEGATION_PROFILE_LABELS,
  DELEGATION_PROFILE_DESCRIPTIONS,
} from '@/lib/types/thread';

export default function NewThreadPage() {
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

      <Card>
        <CardHeader>
          <CardTitle>线程信息</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="title">标题</Label>
            <Input id="title" placeholder="简明描述这个线程的目标" />
          </div>

          <div className="space-y-2">
            <Label htmlFor="objective">目标</Label>
            <Textarea
              id="objective"
              placeholder="详细描述你想达成的目标..."
              rows={4}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="participants">参与者</Label>
            <Input id="participants" placeholder="添加参与者（开发中）" disabled />
          </div>

          <div className="space-y-2">
            <Label htmlFor="delegation">委托档位</Label>
            <Select defaultValue="draft_first">
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
            <Button className="flex-1">创建线程</Button>
            <Button variant="outline" asChild>
              <Link href="/">取消</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
