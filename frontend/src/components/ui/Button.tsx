import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "primary" | "ghost" | "danger";
  size?: "sm" | "md";
  loading?: boolean;
  children: React.ReactNode;
}

const variantClasses = {
  default: "bg-[#1e222b] text-[#e7e9ee] border border-[#2a2f3a] hover:border-[#5b8cff]",
  primary: "bg-[#5b8cff] text-[#06122e] border border-[#5b8cff] font-bold hover:brightness-110",
  ghost:   "bg-transparent text-[#9aa3b2] border border-transparent hover:bg-[#1e222b] hover:text-[#e7e9ee]",
  danger:  "bg-red-950/60 text-[#f87171] border border-red-800/50 hover:bg-red-900/60",
};

const sizeClasses = {
  sm: "px-2.5 py-1 text-[12px]",
  md: "px-3.5 py-2 text-[13px]",
};

export function Button({
  variant = "default",
  size = "md",
  loading = false,
  disabled,
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center gap-1.5 rounded-lg font-semibold cursor-pointer transition-all",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 size={13} className="spin" />}
      {children}
    </button>
  );
}
