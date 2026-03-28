'use client';

import { AppShell } from '@/components/layout/AppShell';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Toaster } from '@/components/ui/toaster';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <TooltipProvider>
      <AppShell>{children}</AppShell>
      <Toaster />
    </TooltipProvider>
  );
}
