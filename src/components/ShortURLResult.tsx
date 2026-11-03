import React from "react";
import { Link2, ExternalLink } from "lucide-react";
import { SketchCard } from "./ui/SketchCard";
import CopyButton from "./CopyButton";
import { ShortenURLResponse } from "../types";

interface ShortURLResultProps {
  result: ShortenURLResponse;
}

export const ShortURLResult: React.FC<ShortURLResultProps> = ({ result }) => {
  return (
    <SketchCard variant="yellow" className="w-full">
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-2 text-stone-700">
          <Link2 className="w-5 h-5 text-amber-700" />
          <span className="font-sketch text-lg font-bold">Your Short Link is Ready!</span>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-white/70 border border-stone-800 rounded">
          <a
            href={result.short_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-amber-800 font-mono font-medium hover:underline flex items-center gap-1.5 break-all"
          >
            {result.short_url}
            <ExternalLink className="w-3.5 h-3.5 inline-block shrink-0" />
          </a>
          <div className="shrink-0">
            <CopyButton text={result.short_url} />
          </div>
        </div>

        <div className="text-xs text-stone-500 truncate">
          <span className="font-semibold">Original:</span> {result.original_url}
        </div>
      </div>
    </SketchCard>
  );
};

export default ShortURLResult;

