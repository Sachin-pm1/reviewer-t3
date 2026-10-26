"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  CloudRain, Mountain, Car, Sun, Footprints, BookOpen, Laptop, Waves,
  Play, Pause, Music2,
} from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GradientText } from "@/components/GradientText";
import { AuraBadge } from "@/components/AuraBadge";
import { api } from "@/lib/api";
import { useAudioPlayer, type PlayerTrack } from "@/lib/audio-player-context";
import type { TrackPick } from "@/lib/types";

const EXPERIENCES = [
  { icon: CloudRain, title: "Rainy Sunday",       mood: "Cozy",       weather: "Rain", time: "Afternoon", energy: 20, color: "from-blue-600/25 to-indigo-600/25", border: "border-blue-500/20", desc: "Blankets, hot chai, and the perfect rain playlist." },
  { icon: Mountain,  title: "Solo Trek",           mood: "Free",       weather: "Clear", time: "Morning", energy: 70, color: "from-teal-600/25 to-emerald-600/25", border: "border-teal-500/20",  desc: "Just you, the mountains, and music that makes you feel infinite." },
  { icon: Car,       title: "Midnight Highway",    mood: "Alive",      weather: "Night", time: "11pm+",   energy: 80, color: "from-purple-600/25 to-blue-600/25",  border: "border-purple-500/20", desc: "Empty roads, city lights behind you, entire world ahead." },
  { icon: Sun,       title: "Creative Morning",   mood: "Inspired",   weather: "Sunny", time: "Early AM", energy: 60, color: "from-yellow-600/25 to-orange-600/25", border: "border-yellow-500/20", desc: "Blank canvas, fresh coffee, and music that sparks ideas." },
  { icon: Footprints, title: "Sunrise Run",        mood: "Powerful",   weather: "Clear", time: "6am",     energy: 90, color: "from-orange-600/25 to-red-600/25",   border: "border-orange-500/20", desc: "Before the world wakes up, you're already winning." },
  { icon: BookOpen,  title: "Reading Retreat",     mood: "Deep",       weather: "Any",   time: "Evening",  energy: 25, color: "from-emerald-600/25 to-teal-600/25", border: "border-emerald-500/20", desc: "Soft background music that lets you disappear into pages." },
  { icon: Laptop,    title: "Deep Work Session",   mood: "Flow",       weather: "Any",   time: "Any",      energy: 50, color: "from-indigo-600/25 to-purple-600/25", border: "border-indigo-500/20", desc: "Enter the zone and stay there. Pure concentration fuel." },
  { icon: Waves,     title: "Weekend Escape",      mood: "Refreshed",  weather: "Breezy", time: "Weekend", energy: 55, color: "from-cyan-600/25 to-blue-600/25",    border: "border-cyan-500/20",   desc: "Leave the week behind. This is your time." },
];

type CardState = { status: "loading" } | { status: "ready"; track: TrackPick } | { status: "error" };

function toPlayerTrack(id: string, t: TrackPick): PlayerTrack | null {
  if (!t.preview_url) return null;
  return { id, name: t.track, artist: t.artist, artworkUrl: t.artwork_url, previewUrl: t.preview_url, externalUrl: t.external_url };
}

export default function AuraDiscovery() {
  const router = useRouter();
  const [hovered, setHovered] = useState<number | null>(null);
  const [tracks, setTracks] = useState<Record<string, CardState>>({});
  const { current, playing, playQueue, toggle } = useAudioPlayer();

  useEffect(() => {
    let cancelled = false;

    for (const exp of EXPERIENCES) {
      setTracks((t) => ({ ...t, [exp.title]: { status: "loading" } }));
      api.catalog
        .experienceTrack({ title: exp.title, mood: exp.mood, desc: exp.desc })
        .then((track) => {
          if (!cancelled) setTracks((t) => ({ ...t, [exp.title]: { status: "ready", track } }));
        })
        .catch(() => {
          if (!cancelled) setTracks((t) => ({ ...t, [exp.title]: { status: "error" } }));
        });
    }

    return () => {
      cancelled = true;
    };
  }, []);

  function playCard(title: string) {
    if (current?.id === title) {
      toggle();
      return;
    }
    const playable = EXPERIENCES
      .map((exp) => {
        const card = tracks[exp.title];
        return card?.status === "ready" ? toPlayerTrack(exp.title, card.track) : null;
      })
      .filter((t): t is PlayerTrack => t !== null);
    const startIndex = playable.findIndex((t) => t.id === title);
    if (startIndex >= 0) playQueue(playable, startIndex);
  }

  function beginExperience(exp: (typeof EXPERIENCES)[number]) {
    const prompt = `I want a musical journey for "${exp.title}" — ${exp.desc} Mood: ${exp.mood.toLowerCase()}, energy around ${exp.energy}/100.`;
    router.push(`/companion?prompt=${encodeURIComponent(prompt)}`);
  }

  return (
    <div className="aura-bg min-h-screen p-4 sm:p-6 lg:p-8 text-white">
      <AuroraBlobs />
      <div className="relative w-full">
        <div className="mb-8">
          <p className="text-white/40 text-[12px] uppercase tracking-widest mb-2 font-bold">Discover Moments</p>
          <h1 className="text-3xl sm:text-4xl font-black mb-2">Discover <GradientText>Experiences,</GradientText><br />Not Just Songs.</h1>
          <p className="text-white/50 text-[14px]">Curated musical experiences for every moment of life — each grounded in a real track from Spotify.</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
          {EXPERIENCES.map((exp, i) => {
            const card = tracks[exp.title];
            return (
              <div
                key={i}
                onMouseEnter={() => setHovered(i)}
                onMouseLeave={() => setHovered(null)}
                className={`glass-card bg-gradient-to-br ${exp.color} ${exp.border} p-6 cursor-pointer transition-all duration-300 ${hovered === i ? "scale-[1.02] border-white/20" : ""}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-11 h-11 rounded-2xl bg-white/10 flex items-center justify-center">
                    <exp.icon size={20} />
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <AuraBadge color="green">{exp.mood}</AuraBadge>
                    <span className="text-[10px] text-white/40">{exp.time}</span>
                  </div>
                </div>
                <h3 className="text-[18px] font-black mb-2">{exp.title}</h3>
                <p className="text-[13px] text-white/60 mb-4 leading-relaxed">{exp.desc}</p>
                <div className="flex items-center gap-3 text-[11px] text-white/40 mb-4">
                  <span className="inline-flex items-center gap-1"><CloudRain size={11} /> {exp.weather}</span>
                </div>

                {/* Real representative track */}
                <div className="rounded-xl bg-black/20 border border-white/5 p-2.5 flex items-center gap-2.5 mb-1">
                  {!card || card.status === "loading" ? (
                    <>
                      <div className="w-9 h-9 rounded-lg bg-white/5 animate-pulse shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="h-2.5 w-3/4 rounded bg-white/10 animate-pulse mb-1.5" />
                        <div className="h-2 w-1/2 rounded bg-white/5 animate-pulse" />
                      </div>
                    </>
                  ) : card.status === "error" || !card.track ? (
                    <p className="text-[11px] text-white/30 py-1">Couldn&apos;t load a preview track right now.</p>
                  ) : (
                    <>
                      {card.track.artwork_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={card.track.artwork_url} alt="" className="w-9 h-9 rounded-lg object-cover shrink-0" />
                      ) : (
                        <div className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center shrink-0">
                          <Music2 size={14} className="text-white/40" />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="text-[12px] font-bold truncate">{card.track.track}</div>
                        <div className="text-[10px] text-white/40 truncate">
                          {card.track.artist}
                          {card.track.source && (
                            <span className={card.track.source === "spotify" ? "text-emerald-400" : "text-white/30"}>
                              {" "}· {card.track.source}
                            </span>
                          )}
                        </div>
                      </div>
                      {card.track.preview_url && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            playCard(exp.title);
                          }}
                          aria-label={current?.id === exp.title && playing ? "Pause preview" : "Play preview"}
                          className="w-7 h-7 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center hover:bg-emerald-500/30 shrink-0"
                        >
                          {current?.id === exp.title && playing ? (
                            <Pause size={11} className="fill-current" />
                          ) : (
                            <Play size={11} className="fill-current" />
                          )}
                        </button>
                      )}
                    </>
                  )}
                </div>

                {hovered === i && (
                  <button
                    onClick={() => beginExperience(exp)}
                    className="mt-3 w-full py-2.5 rounded-xl bg-white/10 text-white text-[13px] font-bold hover:bg-white/20 transition-colors slide-up flex items-center justify-center gap-1.5"
                  >
                    <Play size={13} className="fill-current" /> Begin Experience
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
