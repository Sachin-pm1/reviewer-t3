"use client";

import { useEffect, useState } from "react";
import { Car, TrainFront, Bus, PersonStanding, Music, Music2, SkipBack, Play, Pause, SkipForward } from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import { AuraBadge } from "@/components/AuraBadge";
import { api } from "@/lib/api";
import { useAudioPlayer, type PlayerTrack } from "@/lib/audio-player-context";
import type { TrackPick } from "@/lib/types";

const MODES = [
  { icon: Car,            label: "Driving",    active: true  },
  { icon: TrainFront,     label: "Metro",      active: false },
  { icon: Bus,            label: "Bus",        active: false },
  { icon: PersonStanding, label: "Walking",    active: false },
];

const QUEUE = [
  { title: "Commute Start",  mood: "Settling in",   energy: 55, desc: "Just left home, easing into the drive with a mid-energy track." },
  { title: "Building Energy", mood: "Upbeat",       energy: 76, desc: "Traffic is moving, energy is building — an upbeat pop or dance track." },
  { title: "Peak Traffic",   mood: "Alive",         energy: 92, desc: "Stuck in busy traffic — a high-energy anthem to keep the mood up." },
  { title: "Almost There",   mood: "Feel-good",     energy: 85, desc: "Nearly at the destination — a feel-good track to end the commute on a high." },
];

type CardState = { status: "loading" } | { status: "ready"; track: TrackPick } | { status: "error" };

function toPlayerTrack(id: string, t: TrackPick): PlayerTrack | null {
  if (!t.preview_url) return null;
  return { id, name: t.track, artist: t.artist, artworkUrl: t.artwork_url, previewUrl: t.preview_url, externalUrl: t.external_url };
}

export default function AuraCommute() {
  const [mode, setMode] = useState(0);
  const [tracks, setTracks] = useState<Record<string, CardState>>({});
  const { current: nowPlaying, playing, playQueue, toggle, prev, next } = useAudioPlayer();

  useEffect(() => {
    let cancelled = false;
    for (const slot of QUEUE) {
      setTracks((t) => ({ ...t, [slot.title]: { status: "loading" } }));
      api.catalog
        .experienceTrack({ title: slot.title, mood: slot.mood, desc: slot.desc })
        .then((track) => {
          if (!cancelled) setTracks((t) => ({ ...t, [slot.title]: { status: "ready", track } }));
        })
        .catch(() => {
          if (!cancelled) setTracks((t) => ({ ...t, [slot.title]: { status: "error" } }));
        });
    }
    return () => {
      cancelled = true;
    };
  }, []);

  function playableQueue(): PlayerTrack[] {
    return QUEUE
      .map((slot) => {
        const card = tracks[slot.title];
        return card?.status === "ready" ? toPlayerTrack(slot.title, card.track) : null;
      })
      .filter((t): t is PlayerTrack => t !== null);
  }

  function playSlot(title: string) {
    if (nowPlaying?.id === title) {
      toggle();
      return;
    }
    const playable = playableQueue();
    const startIndex = playable.findIndex((t) => t.id === title);
    if (startIndex >= 0) playQueue(playable, startIndex);
  }

  const isThisQueue = nowPlaying ? QUEUE.some((slot) => slot.title === nowPlaying.id) : false;
  const activeSlot = isThisQueue ? QUEUE.find((slot) => slot.title === nowPlaying!.id) : undefined;
  const current = activeSlot ? tracks[activeSlot.title] : undefined;

  return (
    <div className="aura-bg min-h-screen p-4 sm:p-6 lg:p-8 text-white">
      <AuroraBlobs />
      <div className="relative max-w-3xl mx-auto space-y-6">
        <div>
          <p className="text-white/40 text-[12px] uppercase tracking-widest mb-2 font-bold">Adaptive Mode</p>
          <h1 className="text-3xl sm:text-4xl font-black"><GradientText>Commute Mode</GradientText></h1>
          <p className="text-white/50 text-[14px] mt-2">A real track grounded to each stage of a typical commute — from settling in to arriving.</p>
        </div>

        <div className="glass-card border-white/10 bg-white/[0.03] px-4 py-3 text-[12px] text-white/40">
          This app doesn&apos;t have location or live traffic data — the distance/ETA/traffic card that
          used to be here was invented placeholder content, so it&apos;s gone. The transport mode below is
          just a manual selector; the tracks are real.
        </div>

        {/* Transport mode selector */}
        <div className="flex gap-3">
          {MODES.map((m, i) => (
            <button
              key={i}
              onClick={() => setMode(i)}
              className={`flex-1 glass-card py-3 flex flex-col items-center gap-1.5 transition-all ${mode === i ? "border-emerald-500/50 bg-emerald-500/10" : ""}`}
            >
              <m.icon size={20} className="text-white/80" />
              <span className="text-[11px] font-bold text-white/70">{m.label}</span>
            </button>
          ))}
        </div>

        {/* Now playing */}
        <GlassCard>
          <div className="text-[12px] text-white/40 font-bold uppercase mb-3">Now Playing</div>
          <div className="flex items-center gap-4 mb-4">
            {!isThisQueue || !current || current.status === "loading" ? (
              <>
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shrink-0"><Music size={22} /></div>
                <div className="flex-1 text-[12px] text-white/30">Pick a track from the queue below.</div>
              </>
            ) : current.status === "error" || !current.track ? (
              <>
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center"><Music size={22} /></div>
                <div className="flex-1 text-[12px] text-white/30">Couldn&apos;t load a track right now.</div>
              </>
            ) : (
              <>
                {current.track.artwork_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={current.track.artwork_url} alt="" className="w-14 h-14 rounded-2xl object-cover shrink-0" />
                ) : (
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shrink-0"><Music size={22} /></div>
                )}
                <div className="flex-1 min-w-0">
                  <div className="text-[16px] font-black truncate">{current.track.track}</div>
                  <div className="text-[13px] text-white/50 truncate">
                    {current.track.artist}
                    {current.track.source && (
                      <span className={current.track.source === "spotify" ? "text-emerald-400" : "text-white/30"}> · {current.track.source}</span>
                    )}
                  </div>
                </div>
                {activeSlot && <AuraBadge color="blue">{activeSlot.energy}% energy</AuraBadge>}
              </>
            )}
          </div>
          <div className="h-1.5 bg-white/10 rounded-full mb-4">
            <div className="energy-bar h-1.5 rounded-full" style={{ width: `${activeSlot?.energy ?? 0}%` }} />
          </div>
          <div className="flex items-center justify-center gap-6">
            <button onClick={prev} disabled={!isThisQueue} aria-label="Previous track" className="text-white/50 hover:text-white disabled:opacity-25">
              <SkipBack size={22} className="fill-current" />
            </button>
            <button
              onClick={() => (isThisQueue ? toggle() : playSlot(QUEUE[0].title))}
              aria-label={isThisQueue && playing ? "Pause" : "Play"}
              className="w-12 h-12 rounded-full bg-emerald-500 text-black flex items-center justify-center hover:brightness-110 transition-all"
            >
              {isThisQueue && playing ? <Pause size={18} className="fill-current" /> : <Play size={18} className="fill-current" />}
            </button>
            <button onClick={next} disabled={!isThisQueue} aria-label="Next track" className="text-white/50 hover:text-white disabled:opacity-25">
              <SkipForward size={22} className="fill-current" />
            </button>
          </div>
        </GlassCard>

        {/* Up next */}
        <GlassCard>
          <div className="text-[12px] text-white/40 font-bold uppercase mb-3">Commute Queue</div>
          {QUEUE.map((slot, i) => {
            const card = tracks[slot.title];
            const isActive = nowPlaying?.id === slot.title;
            return (
              <div key={i} onClick={() => playSlot(slot.title)} className={`flex items-center gap-3 py-2.5 border-b border-white/5 last:border-0 cursor-pointer hover:bg-white/5 rounded-lg px-2 -mx-2 transition-colors ${isActive ? "bg-white/5" : ""}`}>
                <span className="text-emerald-400 w-4 text-center flex items-center justify-center shrink-0">
                  {isActive ? (playing ? <Pause size={11} className="fill-current" /> : <Play size={11} className="fill-current" />) : i + 1}
                </span>
                {!card || card.status === "loading" ? (
                  <div className="flex-1"><div className="h-2.5 w-1/2 rounded bg-white/10 animate-pulse mb-1.5" /><div className="h-2 w-1/3 rounded bg-white/5 animate-pulse" /></div>
                ) : card.status === "error" || !card.track ? (
                  <div className="flex-1 text-[12px] text-white/30">{slot.title}</div>
                ) : (
                  <div className="flex-1 min-w-0 flex items-center gap-2">
                    {card.track.artwork_url ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={card.track.artwork_url} alt="" className="w-7 h-7 rounded-md object-cover shrink-0" />
                    ) : (
                      <div className="w-7 h-7 rounded-md bg-white/5 flex items-center justify-center shrink-0"><Music2 size={11} className="text-white/40" /></div>
                    )}
                    <div className="min-w-0">
                      <div className="text-[13px] font-semibold truncate">{card.track.track}</div>
                      <div className="text-[11px] text-white/40 truncate">{card.track.artist}</div>
                    </div>
                  </div>
                )}
                <AuraBadge color="blue">{slot.energy}%</AuraBadge>
              </div>
            );
          })}
        </GlassCard>
      </div>
    </div>
  );
}
