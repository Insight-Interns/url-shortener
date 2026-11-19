export type PlanTier = "free" | "plus" | "pro";

export function normalizePlanTier(tier?: string | null): PlanTier {
  if (tier === "plus") return "plus";
  if (tier === "pro" || tier === "premium" || tier === "admin") return "pro";
  return "free";
}

export const PLAN_DETAILS: Record<PlanTier, { name: string; maxDays: number | null; durations: number[] }> = {
  free: { name: "Free", maxDays: 10, durations: [1, 7, 10] },
  plus: { name: "Plus", maxDays: 30, durations: [1, 7, 10, 30] },
  pro: { name: "Pro", maxDays: null, durations: [1, 7, 10, 30, 0] },
};

export function defaultDurationForPlan(tier: PlanTier): number {
  return tier === "pro" ? 0 : PLAN_DETAILS[tier].maxDays ?? 10;
}
