import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "positive" | "negative" | "neutral" | "mixed" | "warn";
  className?: string;
}

const variantClasses = {
  default:  "bg-[#1e222b] text-[#9aa3b2] border-[#2a2f3a]",
  positive: "bg-emerald-950/50 text-[#34d399] border-emerald-800/40",
  negative: "bg-red-950/50 text-[#f87171] border-red-800/40",
  neutral:  "bg-[#1e222b] text-[#9aa3b2] border-[#2a2f3a]",
  mixed:    "bg-yellow-950/50 text-[#fbbf24] border-yellow-800/40",
  warn:     "bg-yellow-950/50 text-[#fbbf24] border-yellow-800/40",
};

export function Badge({ children, variant = "default", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold border",
        variantClasses[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
