import { cn } from "@/lib/utils";

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}

export function GlassCard({ children, className, style, onClick }: GlassCardProps) {
  return (
    <div
      onClick={onClick}
      style={style}
      className={cn("glass-card p-5", onClick && "cursor-pointer", className)}
    >
      {children}
    </div>
  );
}
