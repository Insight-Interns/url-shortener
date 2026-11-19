import { Check, Crown, Sparkles } from "lucide-react";
import Navbar from "../components/Navbar";
import { SketchCard } from "../components/ui/SketchCard";
import { useAuth } from "../context/AuthContext";
import { normalizePlanTier, PLAN_DETAILS, PlanTier } from "../config/plans";

const planFeatures: Record<PlanTier, string[]> = {
  free: ["Create and manage links", "Choose a lifetime up to 10 days", "View your link history"],
  plus: ["Everything in Free", "Choose a lifetime up to 30 days", "Manage links from your dashboard"],
  pro: ["Everything in Plus", "Choose permanent links", "Choose shorter lifetimes when needed"],
};

export default function PlansPage() {
  const { user } = useAuth();
  const currentTier = normalizePlanTier(user?.tier);

  return (
    <div className="min-h-screen flex flex-col bg-[#faf8f5]">
      <Navbar />
      <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-12">
        <header className="text-center mb-10">
          <div className="inline-flex p-2 bg-amber-100 border-2 border-stone-800 rounded-full mb-3">
            <Crown className="w-6 h-6 text-amber-800" />
          </div>
          <h1 className="font-sketch text-4xl font-bold text-stone-900">Choose your link lifetime</h1>
          <p className="mt-2 text-stone-600">Your current plan is {PLAN_DETAILS[currentTier].name}.</p>
        </header>

        <div className="grid gap-5 md:grid-cols-3">
          {(["free", "plus", "pro"] as PlanTier[]).map((tier) => {
            const plan = PLAN_DETAILS[tier];
            const isCurrent = tier === currentTier;
            return (
              <SketchCard key={tier} variant={tier === "plus" ? "yellow" : "white"} className="flex flex-col p-6">
                <div className="flex items-center justify-between">
                  <h2 className="font-sketch text-2xl font-bold text-stone-900">{plan.name}</h2>
                  {tier === "pro" && <Sparkles className="w-5 h-5 text-amber-700" />}
                </div>
                <p className="mt-3 min-h-12 text-stone-700">
                  {plan.maxDays === null ? "Links can stay active permanently." : `Links can stay active for up to ${plan.maxDays} days.`}
                </p>
                <ul className="my-6 flex-1 space-y-3">
                  {planFeatures[tier].map((feature) => (
                    <li key={feature} className="flex items-start gap-2 text-sm text-stone-700">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-green-700" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <button
                  type="button"
                  disabled
                  className="w-full rounded border-2 border-stone-800 px-4 py-2 font-sketch font-semibold text-stone-800 disabled:cursor-not-allowed disabled:opacity-70"
                  title="Plan upgrades will be available when billing is configured"
                >
                  {isCurrent ? "Current plan" : "Upgrade options coming soon"}
                </button>
              </SketchCard>
            );
          })}
        </div>

        <p className="mt-6 text-center text-sm text-stone-500">
          Plus and Pro are shown for plan comparison. Paid upgrades are not enabled yet.
        </p>
      </main>
    </div>
  );
}
