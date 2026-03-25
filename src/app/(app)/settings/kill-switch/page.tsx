'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, ShieldAlert, ShieldX } from 'lucide-react';
import Link from 'next/link';
import { KillSwitchButton } from '@/components/delegation';
import { useState } from 'react';

export default function KillSwitchPage() {
  const [globalActive, setGlobalActive] = useState(false);

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <Button variant="ghost" size="sm" asChild className="mb-4">
          <Link href="/settings/delegation">
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回设置
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Kill Switch 管理</h1>
          <p className="text-muted-foreground mt-1">管理各层级的 Kill Switch</p>
        </div>
      </div>

      <div className="space-y-6">
        {/* Global Kill Switch */}
        <Card className="border-red-200 bg-red-50/30">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-100">
                  {globalActive ? (
                    <ShieldX className="h-5 w-5 text-red-600" />
                  ) : (
                    <ShieldAlert className="h-5 w-5 text-red-600" />
                  )}
                </div>
                <div>
                  <CardTitle className="text-red-800">全局 Kill Switch</CardTitle>
                  <CardDescription className="text-red-600">
                    紧急暂停所有自动化操作
                  </CardDescription>
                </div>
              </div>
              <KillSwitchButton
                level="global"
                isActive={globalActive}
                onToggle={setGlobalActive}
              />
            </div>
          </CardHeader>
        </Card>

        {/* Profile Level Kill Switch */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">委托档位 Kill Switch</CardTitle>
            <CardDescription>暂停特定委托档位的自动化操作</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              档位级 Kill Switch 管理开发中...
            </div>
          </CardContent>
        </Card>

        {/* Thread Level Kill Switch */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">线程 Kill Switch</CardTitle>
            <CardDescription>暂停特定线程的自动化操作</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              线程级 Kill Switch 管理开发中...
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
