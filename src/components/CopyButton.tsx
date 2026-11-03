import React, { useState } from "react";
import { Copy, Check } from "lucide-react";
import { SketchButton } from "./ui/SketchButton";

interface CopyButtonProps {
  text: string;
}

export const CopyButton: React.FC<CopyButtonProps> = ({ text }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <SketchButton
      type="button"
      size="sm"
      variant={copied ? "secondary" : "primary"}
      onClick={handleCopy}
    >
      {copied ? (
        <>
          <Check className="w-4 h-4 text-emerald-600" />
          <span className="text-emerald-700">Copied!</span>
        </>
      ) : (
        <>
          <Copy className="w-4 h-4" />
          <span>Copy</span>
        </>
      )}
    </SketchButton>
  );
};

export default CopyButton;

