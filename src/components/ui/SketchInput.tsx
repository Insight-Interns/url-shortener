import React, { useEffect, useRef, useState } from "react";
import rough from "roughjs";

interface SketchInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const SketchInput: React.FC<SketchInputProps> = ({
  label,
  error,
  className = "",
  ...props
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    const canvas = canvasRef.current;
    if (!container || !canvas) return;

    const draw = () => {
      const rect = container.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const width = Math.max(1, rect.width);
      const height = Math.max(1, rect.height);

      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;

      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      ctx.scale(dpr, dpr);

      const rc = rough.canvas(canvas);
      rc.rectangle(2, 2, width - 4, height - 4, {
        roughness: isFocused ? 1.5 : 1,
        bowing: 1.2,
        stroke: error ? "#dc2626" : isFocused ? "#2563eb" : "#1c1917",
        strokeWidth: isFocused ? 2.5 : 1.8,
        fill: "#ffffff",
        fillStyle: "solid",
      });
    };

    draw();

    const resizeObserver = new ResizeObserver(() => draw());
    resizeObserver.observe(container);
    return () => resizeObserver.disconnect();
  }, [isFocused, error]);

  return (
    <div className="w-full">
      {label && (
        <label className="block mb-1 text-sm font-sketch text-stone-800 tracking-wide font-semibold">
          {label}
        </label>
      )}
      <div ref={containerRef} className="relative w-full">
        <canvas
          ref={canvasRef}
          className="absolute inset-0 pointer-events-none -z-10"
        />
        <input
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className={`w-full bg-transparent px-4 py-2.5 text-stone-900 placeholder:text-stone-400 focus:outline-none text-base ${className}`}
          {...props}
        />
      </div>
      {error && (
        <p className="mt-1 text-xs text-red-600 font-sketch">{error}</p>
      )}
    </div>
  );
};

