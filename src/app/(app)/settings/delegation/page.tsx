'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ShieldAlert } from 'lucide-react';
import { RELATIONSHIP_TEMPLATES } from '@/lib/types/delegation';
import { KillSwitchButton, ProfileCard, DelegationSlider } from '@/components/delegation';
import { useState } from 'react';
import type { DelegationProfile } from '@/lib/types/thread';

export default function DelegationPage() {
  const [globalKillSwitch, setGlobalKillSwitch] = useState(false);
  const [selectedProfile, setSelectedProfile] = useState<DelegationProfile>('draft_first');

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">委托档位管理</h1>
        <p className="text-muted-foreground mt-1">配置不同关系类型的默认委托档位</p>
      </div>

      {/* Kill Switch Section */}
      <Card className="mb-6 border-red-200 bg-red-50/30">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-100">
                <ShieldAlert className="h-5 w-5 text-red-600" />
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
              isActive={globalKillSwitch}
              onToggle={setGlobalKillSwitch}
            />
          </div>
        </CardHeader>
      </Card>

      {/* Delegation Slider Demo */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">委托档位选择器</CardTitle>
          <CardDescription>选择全局默认委托档位</CardDescription>
        </CardHeader>
        <CardContent>
          <DelegationSlider
            value={selectedProfile}
            onChange={setSelectedProfile}
          />
        </CardContent>
      </Card>

      {/* Relationship Templates */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">关系模板</h2>
        <div className="grid gap-4">
          {RELATIONSHIP_TEMPLATES.map((template) => (
            <ProfileCard
              key={template.id}
              id={template.id}
              name={template.name}
              description={template.description}
              relationshipClass={template.relationshipClass}
              defaultProfile={template.defaultProfile}
              enabled={true}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
