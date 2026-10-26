import { cn } from "@/lib/utils";

interface ProgressBarProps {
  value: number; // 0..1
  className?: string;
  showLabel?: boolean;
}

export function ProgressBar({ value, className, showLabel }: ProgressBarProps) {
  const pct = Math.round(value * 100);
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div className="flex-1 h-1.5 bg-[#1e222b] border border-[#2a2f3a] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{
            width: `${pct}%`,
            background: "linear-gradient(90deg, #5b8cff, #34d399)",
          }}
        />
      </div>
      {showLabel && (
        <span className="text-[11px] text-[#9aa3b2] w-8 text-right">{pct}%</span>
      )}
    </div>
  );
}
