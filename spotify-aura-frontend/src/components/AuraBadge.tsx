import { cn } from "@/lib/utils";

const COLORS: Record<string, string> = {
  green:  "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  blue:   "bg-blue-500/15 text-blue-400 border-blue-500/30",
  purple: "bg-purple-500/15 text-purple-400 border-purple-500/30",
  pink:   "bg-pink-500/15 text-pink-400 border-pink-500/30",
  orange: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  teal:   "bg-teal-500/15 text-teal-400 border-teal-500/30",
};

export function AuraBadge({
  children,
  color = "green",
  className,
}: {
  children: React.ReactNode;
  color?: keyof typeof COLORS;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold border",
        COLORS[color],
        className
      )}
    >
      {children}
    </span>
  );
}
