import React, { useEffect, useRef, useState } from "react";
import rough from "roughjs";

interface SketchButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "danger";
  size?: "sm" | "md" | "lg";
  className?: string;
}

const bgColors = {
  primary: "#fed7aa", // warm amber/orange
  secondary: "#f5f5f4", // warm stone
  danger: "#fecaca", // light red
};

const hoverBgColors = {
  primary: "#fdba74",
  secondary: "#e7e5e4",
  danger: "#fca5a5",
};

export const SketchButton: React.FC<SketchButtonProps> = ({
  children,
  variant = "primary",
  size = "md",
  className = "",
  disabled = false,
  ...props
}) => {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const button = buttonRef.current;
    const canvas = canvasRef.current;
    if (!button || !canvas) return;

    const draw = () => {
      const rect = button.getBoundingClientRect();
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
        roughness: isHovered ? 1.8 : 1.2,
        bowing: 1.5,
        stroke: "#1c1917",
        strokeWidth: 2,
        fill: disabled
          ? "#e7e5e4"
          : isHovered
          ? hoverBgColors[variant]
          : bgColors[variant],
        fillStyle: "solid",
      });
    };

    draw();

    const resizeObserver = new ResizeObserver(() => draw());
    resizeObserver.observe(button);
    return () => resizeObserver.disconnect();
  }, [variant, isHovered, disabled]);

  const sizeClasses = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-5 py-2.5 text-base font-medium",
    lg: "px-7 py-3 text-lg font-medium",
  };

  return (
    <button
      ref={buttonRef}
      onMouseEnter={() => !disabled && setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      disabled={disabled}
      className={`relative inline-flex items-center justify-center font-sketch text-stone-900 cursor-pointer transition-transform active:translate-y-0.5 disabled:opacity-60 disabled:cursor-not-allowed ${sizeClasses[size]} ${className}`}
      {...props}
    >
      <canvas
        ref={canvasRef}
        className="absolute inset-0 pointer-events-none -z-10"
      />
      <span className="relative z-10 flex items-center gap-2">{children}</span>
    </button>
  );
};

