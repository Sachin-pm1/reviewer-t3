import { cn } from "@/lib/utils";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: boolean;
  style?: React.CSSProperties;
}

export function Card({ children, className, padding = true, style }: CardProps) {
  return (
    <div
      className={cn(
        "bg-[#171a21] border border-[#2a2f3a] rounded-[10px]",
        padding && "p-4",
        className
      )}
      style={style}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("flex items-center justify-between mb-3", className)}>
      {children}
    </div>
  );
}

export function CardTitle({ children }: { children: React.ReactNode }) {
  return <h3 className="text-[13px] font-bold text-[#e7e9ee] uppercase tracking-wider">{children}</h3>;
}
