import React, { useEffect, useRef } from "react";
import rough from "roughjs";

interface SketchCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: "white" | "yellow" | "blue" | "pink" | "green";
  roughness?: number;
  bowing?: number;
  className?: string;
}

const colorMap = {
  white: "#ffffff",
  yellow: "#fffbeb",
  blue: "#eff6ff",
  pink: "#fdf2f8",
  green: "#f0fdf4",
};

export const SketchCard: React.FC<SketchCardProps> = ({
  children,
  variant = "white",
  roughness = 1.2,
  bowing = 1.5,
  className = "",
  ...props
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

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
        roughness,
        bowing,
        stroke: "#1c1917",
        strokeWidth: 2,
        fill: colorMap[variant],
        fillStyle: "solid",
      });
    };

    draw();

    const resizeObserver = new ResizeObserver(() => draw());
    resizeObserver.observe(container);
    return () => resizeObserver.disconnect();
  }, [variant, roughness, bowing]);

  return (
    <div ref={containerRef} className={`relative p-6 ${className}`} {...props}>
      <canvas
        ref={canvasRef}
        className="absolute inset-0 pointer-events-none -z-10"
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
};

