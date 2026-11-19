import React, { useEffect, useState } from "react";
import { LinkIcon, Sparkles } from "lucide-react";
import { SketchCard } from "./ui/SketchCard";
import { SketchInput } from "./ui/SketchInput";
import { SketchButton } from "./ui/SketchButton";
import { ShortenURLRequest } from "../types";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { defaultDurationForPlan, normalizePlanTier, PLAN_DETAILS } from "../config/plans";

interface URLFormProps {
  onSubmit: (data: ShortenURLRequest) => Promise<void>;
  isLoading: boolean;
}

export const URLForm: React.FC<URLFormProps> = ({ onSubmit, isLoading }) => {
  const { user } = useAuth();
  const planTier = normalizePlanTier(user?.tier);
  const plan = PLAN_DETAILS[planTier];
  const [url, setUrl] = useState("");
  const [customAlias, setCustomAlias] = useState("");
  const [expiresInDays, setExpiresInDays] = useState(defaultDurationForPlan(planTier));
  const [error, setError] = useState("");

  useEffect(() => {
    setExpiresInDays(defaultDurationForPlan(planTier));
  }, [planTier]);

  const validateUrl = (value: string): boolean => {
    try {
      new URL(value);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!url.trim()) {
      setError("Please enter a valid URL.");
      return;
    }

    let normalizedUrl = url.trim();
    if (!normalizedUrl.startsWith("http://") && !normalizedUrl.startsWith("https://")) {
      normalizedUrl = `https://${normalizedUrl}`;
    }

    if (!validateUrl(normalizedUrl)) {
      setError("Please enter a valid URL (e.g., https://example.com).");
      return;
    }

    await onSubmit({
      long_url: normalizedUrl,
      custom_alias: customAlias.trim() || undefined,
      expires_in_days: expiresInDays,
    });
  };

  return (
    <SketchCard variant="white" className="w-full">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex items-center gap-2 mb-1">
          <LinkIcon className="w-5 h-5 text-stone-800" />
          <h2 className="text-xl font-sketch font-bold text-stone-900">
            Shorten a Long Link
          </h2>
        </div>

        <SketchInput
          label="Destination URL *"
          type="text"
          placeholder="https://very-long-url.com/some/path"
          value={url}
          onChange={(e) => {
            setUrl(e.target.value);
            if (error) setError("");
          }}
          error={error}
          disabled={isLoading}
        />

        <div>
          <label htmlFor="link-duration" className="mb-1 block text-sm font-sketch font-semibold text-stone-800">
            Link stays active for
          </label>
          <select
            id="link-duration"
            value={expiresInDays}
            onChange={(event) => setExpiresInDays(Number(event.target.value))}
            disabled={isLoading}
            className="w-full rounded border-2 border-stone-800 bg-white px-3 py-2 text-sm text-stone-900"
          >
            {plan.durations.map((days) => (
              <option key={days} value={days}>
                {days === 0 ? "Never expires (Pro)" : `${days} ${days === 1 ? "day" : "days"}`}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-stone-600">
            {plan.maxDays === null ? "Pro links may stay active permanently." : `${plan.name} links can be active for up to ${plan.maxDays} days.`}{" "}
            <Link to="/plans" className="font-semibold text-amber-800 underline">View plans</Link>
          </p>
        </div>

        <SketchInput
          label="Custom Alias (optional)"
          type="text"
          placeholder="my-custom-link"
          value={customAlias}
          onChange={(e) => setCustomAlias(e.target.value)}
          disabled={isLoading}
        />

        <div className="pt-2">
          <SketchButton
            type="submit"
            variant="primary"
            size="md"
            className="w-full"
            disabled={isLoading}
          >
            <Sparkles className="w-4 h-4" />
            <span>{isLoading ? "Shortening..." : "Shorten URL"}</span>
          </SketchButton>
        </div>
      </form>
    </SketchCard>
  );
};

export default URLForm;

