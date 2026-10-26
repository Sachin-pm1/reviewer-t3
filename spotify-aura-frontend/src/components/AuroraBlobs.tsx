export function AuroraBlobs() {
  return (
    <div className="pointer-events-none select-none" aria-hidden>
      <div className="aurora-blob w-[600px] h-[600px] bg-purple-600/30 -top-40 -left-40" style={{ animationDelay: "0s" }} />
      <div className="aurora-blob w-[500px] h-[500px] bg-blue-500/25 top-1/3 -right-32" style={{ animationDelay: "3s" }} />
      <div className="aurora-blob w-[400px] h-[400px] bg-emerald-500/20 bottom-0 left-1/4" style={{ animationDelay: "1.5s" }} />
      <div className="aurora-blob w-[300px] h-[300px] bg-pink-500/20 top-1/2 left-1/2" style={{ animationDelay: "4.5s" }} />
    </div>
  );
}
