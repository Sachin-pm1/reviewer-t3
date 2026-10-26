"use client";

import { useEffect, useState } from "react";
import { Sunrise, Car, Laptop, UtensilsCrossed, Dumbbell, Sunset, Moon, Bot, Play, Pause, Pencil, ChevronUp, ChevronDown, Music2 } from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import { AuraBadge } from "@/components/AuraBadge";
import { api } from "@/lib/api";
import { useAudioPlayer, type PlayerTrack } from "@/lib/audio-player-context";
import type { TrackPick } from "@/lib/types";

const MOMENTS = [
  {
    time: "7:00 AM", icon: Sunrise, title: "Morning Calm", mood: "Peaceful", energy: 30,
    context: "Woke up, light rain outside", style: "Acoustic Guitar & Piano",
    aiReason: "Your sleep was lighter than usual. Starting gentle to ease you into the day.",
    outcome: "Calm start, mental clarity", color: "#F97316", active: false,
  },
  {
    time: "8:15 AM", icon: Car, title: "Commute Drive", mood: "Energized", energy: 65,
    context: "Driving to office · 28 min", style: "Upbeat Pop & Bollywood",
    aiReason: "Traffic is moderate today. Upbeat tracks keep you alert and positive.",
    outcome: "Arrive focused and positive", color: "#1DB954", active: true,
  },
  {
    time: "10:00 AM", icon: Laptop, title: "Deep Focus Block", mood: "Focused", energy: 55,
    context: "3 back-to-back meetings then solo work", style: "Instrumental Lo-fi",
    aiReason: "Calendar shows intense morning. Instrumental music maintains concentration.",
    outcome: "Peak cognitive performance", color: "#3B82F6", active: false,
  },
  {
    time: "1:00 PM", icon: UtensilsCrossed, title: "Lunch Reset", mood: "Relaxed", energy: 38,
    context: "Break time · canteen or outside", style: "Chill Indie & Soul",
    aiReason: "Mid-day reset lowers cortisol. Softer music aids digestion and recovery.",
    outcome: "Recharged for afternoon", color: "#14B8A6", active: false,
  },
  {
    time: "6:00 PM", icon: Dumbbell, title: "Workout Boost", mood: "Pumped", energy: 95,
    context: "Gym session · 60 min", style: "EDM & Power Anthems",
    aiReason: "Heart rate data from yesterday's workout informs BPM selection.",
    outcome: "Maximum performance output", color: "#EC4899", active: false,
  },
  {
    time: "8:30 PM", icon: Sunset, title: "Evening Reflection", mood: "Reflective", energy: 35,
    context: "Home · dinner · wind down", style: "R&B, Soul & Jazz",
    aiReason: "Day is winding down. Emotional music helps process the day's events.",
    outcome: "Emotional processing & calm", color: "#8B5CF6", active: false,
  },
  {
    time: "11:00 PM", icon: Moon, title: "Sleep Journey", mood: "Sleepy", energy: 10,
    context: "Bedtime routine", style: "432Hz Sleep Tones & Nature",
    aiReason: "Binaural beats at delta frequency proven to aid sleep onset.",
    outcome: "Deep restorative sleep", color: "#6366F1", active: false,
  },
];

type CardState = { status: "loading" } | { status: "ready"; track: TrackPick } | { status: "error" };

function toPlayerTrack(id: string, t: TrackPick): PlayerTrack | null {
  if (!t.preview_url) return null;
  return { id, name: t.track, artist: t.artist, artworkUrl: t.artwork_url, previewUrl: t.preview_url, externalUrl: t.external_url };
}

export default function AuraSoundtrack() {
  const [expanded, setExpanded] = useState<number | null>(1);
  const [tracks, setTracks] = useState<Record<string, CardState>>({});
  const { current, playing, playQueue, toggle } = useAudioPlayer();

  useEffect(() => {
    let cancelled = false;
    for (const m of MOMENTS) {
      setTracks((t) => ({ ...t, [m.title]: { status: "loading" } }));
      api.catalog
        .experienceTrack({ title: m.title, mood: m.mood, desc: `${m.context}. Music style: ${m.style}.` })
        .then((track) => {
          if (!cancelled) setTracks((t) => ({ ...t, [m.title]: { status: "ready", track } }));
        })
        .catch(() => {
          if (!cancelled) setTracks((t) => ({ ...t, [m.title]: { status: "error" } }));
        });
    }
    return () => {
      cancelled = true;
    };
  }, []);

  function playMoment(title: string) {
    if (current?.id === title) {
      toggle();
      return;
    }
    const playable = MOMENTS
      .map((m) => {
        const card = tracks[m.title];
        return card?.status === "ready" ? toPlayerTrack(m.title, card.track) : null;
      })
      .filter((t): t is PlayerTrack => t !== null);
    const startIndex = playable.findIndex((t) => t.id === title);
    if (startIndex >= 0) playQueue(playable, startIndex);
  }

  return (
    <div className="aura-bg min-h-screen p-6 text-white">
      <AuroraBlobs />
      <div className="relative max-w-4xl mx-auto">
        <div className="mb-8">
          <p className="text-white/40 text-[12px] uppercase tracking-widest mb-2 font-bold">Monday · Jun 30</p>
          <h1 className="text-4xl font-black mb-2">
            Today&apos;s <GradientText>Life Soundtrack</GradientText>
          </h1>
          <p className="text-white/50 text-[14px]">Your AI-planned musical journey from morning to midnight.</p>
        </div>

        <div className="flex gap-8">
          {/* Timeline */}
          <div className="flex-1 space-y-3">
            {MOMENTS.map((m, i) => (
              <div key={i} className="relative">
                {/* Connector line */}
                {i < MOMENTS.length - 1 && (
                  <div
                    className="absolute left-[27px] top-[60px] w-0.5 h-6 z-10"
                    style={{ background: `linear-gradient(${m.color}, ${MOMENTS[i + 1].color})` }}
                  />
                )}

                <GlassCard
                  className={`cursor-pointer transition-all duration-300 ${m.active ? "border-emerald-500/40 bg-emerald-500/5" : ""} ${expanded === i ? "border-white/20" : ""}`}
                  onClick={() => setExpanded(expanded === i ? null : i)}
                >
                  <div className="flex items-center gap-4">
                    <div
                      className="w-11 h-11 rounded-2xl flex items-center justify-center shrink-0"
                      style={{ background: `${m.color}25`, border: `1px solid ${m.color}40` }}
                    >
                      <m.icon size={18} style={{ color: m.color }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-[14px] font-bold">{m.title}</span>
                        {m.active && <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 dot-ping" />}
                      </div>
                      <div className="text-[11px] text-white/40">{m.time} · {m.context}</div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <div className="text-right">
                        <div className="text-[10px] text-white/40 mb-1">Energy</div>
                        <div className="w-16 h-1.5 bg-white/10 rounded-full">
                          <div className="energy-bar h-1.5 rounded-full" style={{ width: `${m.energy}%` }} />
                        </div>
                      </div>
                      <AuraBadge color={m.mood === "Pumped" || m.mood === "Energized" ? "green" : m.mood === "Focused" ? "blue" : "purple"}>
                        {m.mood}
                      </AuraBadge>
                      <div className="text-white/30">
                        {expanded === i ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      </div>
                    </div>
                  </div>

                  {expanded === i && (() => {
                    const card = tracks[m.title];
                    const previewUrl = card?.status === "ready" ? card.track.preview_url : null;
                    const isActive = current?.id === m.title;
                    return (
                    <div className="mt-4 pt-4 border-t border-white/5 grid grid-cols-2 gap-4 slide-up">
                      <div>
                        <div className="text-[11px] text-white/40 uppercase font-bold mb-1">Music Style</div>
                        <div className="text-[13px] font-semibold">{m.style}</div>
                      </div>
                      <div>
                        <div className="text-[11px] text-white/40 uppercase font-bold mb-1">Expected Outcome</div>
                        <div className="text-[13px] font-semibold text-emerald-400">{m.outcome}</div>
                      </div>
                      <div className="col-span-2">
                        <div className="text-[11px] text-white/40 uppercase font-bold mb-1">Representative Track</div>
                        <div className="rounded-xl bg-black/20 border border-white/5 p-2.5 flex items-center gap-2.5">
                          {!card || card.status === "loading" ? (
                            <>
                              <div className="w-9 h-9 rounded-lg bg-white/5 animate-pulse shrink-0" />
                              <div className="flex-1 min-w-0">
                                <div className="h-2.5 w-3/4 rounded bg-white/10 animate-pulse mb-1.5" />
                                <div className="h-2 w-1/2 rounded bg-white/5 animate-pulse" />
                              </div>
                            </>
                          ) : card.status === "error" || !card.track ? (
                            <p className="text-[11px] text-white/30 py-1">Couldn&apos;t load a track right now.</p>
                          ) : (
                            <>
                              {card.track.artwork_url ? (
                                // eslint-disable-next-line @next/next/no-img-element
                                <img src={card.track.artwork_url} alt="" className="w-9 h-9 rounded-lg object-cover shrink-0" />
                              ) : (
                                <div className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center shrink-0"><Music2 size={14} className="text-white/40" /></div>
                              )}
                              <div className="flex-1 min-w-0">
                                <div className="text-[12px] font-bold truncate">{card.track.track}</div>
                                <div className="text-[10px] text-white/40 truncate">
                                  {card.track.artist}
                                  {card.track.source && (
                                    <span className={card.track.source === "spotify" ? "text-emerald-400" : "text-white/30"}> · {card.track.source}</span>
                                  )}
                                </div>
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                      <div className="col-span-2">
                        <div className="text-[11px] text-white/40 uppercase font-bold mb-1 flex items-center gap-1">
                          <Bot size={12} /> Why Aura chose this
                        </div>
                        <p className="text-[13px] text-white/70 leading-relaxed">{m.aiReason}</p>
                      </div>
                      <div className="col-span-2 flex gap-2">
                        <button
                          onClick={() => previewUrl && playMoment(m.title)}
                          disabled={!previewUrl}
                          className="flex-1 py-2 rounded-xl text-[12px] font-bold text-emerald-400 bg-emerald-500/15 hover:bg-emerald-500/25 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-1.5"
                        >
                          {isActive && playing ? (
                            <><Pause size={12} className="fill-current" /> Playing…</>
                          ) : (
                            <><Play size={12} className="fill-current" /> Play Now</>
                          )}
                        </button>
                        <button className="flex-1 py-2 rounded-xl text-[12px] font-bold text-white/60 bg-white/5 hover:bg-white/10 transition-colors flex items-center justify-center gap-1.5">
                          <Pencil size={12} /> Edit This Moment
                        </button>
                      </div>
                    </div>
                    );
                  })()}
                </GlassCard>
              </div>
            ))}
          </div>

          {/* Energy graph (right sidebar) */}
          <div className="w-36 shrink-0">
            <div className="sticky top-0 pt-2">
              <div className="text-[11px] text-white/40 font-bold uppercase mb-4">Energy</div>
              <div className="relative h-[560px] flex items-end">
                <div className="absolute inset-0 flex items-end justify-center gap-0.5">
                  {MOMENTS.map((m, i) => (
                    <div
                      key={i}
                      className="flex-1 rounded-t-md transition-all duration-700 relative group"
                      style={{
                        height: `${m.energy}%`,
                        background: `linear-gradient(to top, ${m.color}80, ${m.color}30)`,
                        border: `1px solid ${m.color}40`,
                      }}
                    >
                      <div className="absolute -top-5 left-1/2 -translate-x-1/2 text-[9px] text-white/50 font-bold opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                        {m.energy}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="text-[10px] text-white/30 text-center mt-2">Daily Arc</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
