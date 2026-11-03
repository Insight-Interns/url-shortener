import React, { useState } from "react";
import { LinkIcon, Sparkles } from "lucide-react";
import { SketchCard } from "./ui/SketchCard";
import { SketchInput } from "./ui/SketchInput";
import { SketchButton } from "./ui/SketchButton";
import { ShortenURLRequest } from "../types";

interface URLFormProps {
  onSubmit: (data: ShortenURLRequest) => Promise<void>;
  isLoading: boolean;
}

export const URLForm: React.FC<URLFormProps> = ({ onSubmit, isLoading }) => {
  const [url, setUrl] = useState("");
  const [customAlias, setCustomAlias] = useState("");
  const [error, setError] = useState("");

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
      url: normalizedUrl,
      custom_alias: customAlias.trim() || undefined,
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

