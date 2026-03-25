/**
 * Pack Logic 模块导出
 */

export { TimeCoordinationPack, timeCoordinationPack } from './time_coordination.js';
export { InfoCollectionPack, infoCollectionPack } from './info_collection.js';
export { FollowUpPack, followUpPack } from './follow_up.js';
export type { CapabilityPack } from './time_coordination.js';

import type { ThreadContext, ActionPlan } from '../../types/index.js';
import type { CapabilityPack } from './time_coordination.js';
import { timeCoordinationPack } from './time_coordination.js';
import { infoCollectionPack } from './info_collection.js';
import { followUpPack } from './follow_up.js';

export class PackRegistry {
  private packs: Map<string, CapabilityPack> = new Map();

  constructor() {
    this.register(timeCoordinationPack);
    this.register(infoCollectionPack);
    this.register(followUpPack);
  }

  register(pack: CapabilityPack): void {
    this.packs.set(pack.id, pack);
  }

  getPack(id: string): CapabilityPack | undefined {
    return this.packs.get(id);
  }

  findBestPack(context: ThreadContext): CapabilityPack | undefined {
    let bestPack: CapabilityPack | undefined;
    let bestScore = 0;

    for (const pack of this.packs.values()) {
      const score = pack.canHandle(context);
      if (score > bestScore) {
        bestScore = score;
        bestPack = pack;
      }
    }

    return bestScore >= 0.5 ? bestPack : undefined;
  }

  async generatePlanWithBestPack(context: ThreadContext): Promise<ActionPlan | undefined> {
    const pack = this.findBestPack(context);
    if (!pack) return undefined;
    return pack.generatePlan(context);
  }

  listPacks(): CapabilityPack[] {
    return Array.from(this.packs.values());
  }
}

export const packRegistry = new PackRegistry();
export default packRegistry;
