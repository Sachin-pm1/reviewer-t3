"use client";

import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, X, Music2 } from "lucide-react";
import { useAudioPlayer } from "@/lib/audio-player-context";

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function MiniPlayer() {
  const { current, queue, playing, volume, progress, duration, toggle, next, prev, setVolume, seek, close } =
    useAudioPlayer();

  if (!current) return null;

  const pct = duration > 0 ? (progress / duration) * 100 : 0;

  return (
    <div className="fixed bottom-0 inset-x-0 z-[60] border-t border-white/10 bg-black/90 backdrop-blur-xl">
      <div
        role="slider"
        aria-label="Seek"
        aria-valuemin={0}
        aria-valuemax={duration}
        aria-valuenow={progress}
        tabIndex={0}
        onClick={(e) => {
          const rect = e.currentTarget.getBoundingClientRect();
          seek(Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width)));
        }}
        onKeyDown={(e) => {
          if (e.key === "ArrowRight") seek(Math.min(1, (progress + 3) / (duration || 1)));
          if (e.key === "ArrowLeft") seek(Math.max(0, (progress - 3) / (duration || 1)));
        }}
        className="h-1.5 bg-white/10 cursor-pointer group"
      >
        <div className="h-full bg-emerald-400 group-hover:bg-emerald-300 transition-colors" style={{ width: `${pct}%` }} />
      </div>

      <div className="flex items-center gap-3 px-3 sm:px-4 py-2.5 max-w-6xl mx-auto">
        {current.artworkUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={current.artworkUrl} alt="" className="w-10 h-10 rounded-lg object-cover shrink-0" />
        ) : (
          <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center shrink-0"><Music2 size={16} className="text-white/30" /></div>
        )}

        <div className="min-w-0 flex-1 sm:flex-none sm:w-44">
          <div className="text-[13px] font-bold text-white truncate">{current.name}</div>
          <div className="text-[11px] text-white/40 truncate">{current.artist}</div>
        </div>

        <span className="hidden md:inline text-[10px] text-white/30 tabular-nums w-20 text-center shrink-0">
          {formatTime(progress)} / {formatTime(duration)}
        </span>

        <div className="flex items-center gap-1 mx-auto sm:mx-0">
          <button
            onClick={prev}
            disabled={queue.length < 2}
            aria-label="Previous track"
            className="w-8 h-8 flex items-center justify-center text-white/60 hover:text-white disabled:opacity-25 disabled:hover:text-white/60 transition-colors"
          >
            <SkipBack size={16} className="fill-current" />
          </button>
          <button
            onClick={toggle}
            aria-label={playing ? "Pause" : "Play"}
            className="w-9 h-9 rounded-full bg-emerald-500 text-black flex items-center justify-center hover:brightness-110 transition-all shrink-0"
          >
            {playing ? <Pause size={16} className="fill-current" /> : <Play size={16} className="fill-current ml-0.5" />}
          </button>
          <button
            onClick={next}
            disabled={queue.length < 2}
            aria-label="Next track"
            className="w-8 h-8 flex items-center justify-center text-white/60 hover:text-white disabled:opacity-25 disabled:hover:text-white/60 transition-colors"
          >
            <SkipForward size={16} className="fill-current" />
          </button>
        </div>

        <div className="hidden sm:flex items-center gap-1.5 w-28 shrink-0">
          <button
            onClick={() => setVolume(volume > 0 ? 0 : 0.8)}
            aria-label={volume > 0 ? "Mute" : "Unmute"}
            className="text-white/50 hover:text-white shrink-0"
          >
            {volume > 0 ? <Volume2 size={15} /> : <VolumeX size={15} />}
          </button>
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={volume}
            onChange={(e) => setVolume(parseFloat(e.target.value))}
            aria-label="Volume"
            className="w-full accent-emerald-500 h-1"
          />
        </div>

        <button onClick={close} aria-label="Close player" className="text-white/30 hover:text-white shrink-0 ml-1">
          <X size={16} />
        </button>
      </div>
    </div>
  );
}
