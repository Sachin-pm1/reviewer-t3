"use client";

import { useEffect, useState } from "react";
import { Dumbbell, Music, Bot } from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import { AuraBadge } from "@/components/AuraBadge";
import { api } from "@/lib/api";
import type { TrackPick } from "@/lib/types";

const ZONES = [
  { label: "Warm Up",   range: "< 100 BPM",   music: "Upbeat Pop" },
  { label: "Cardio",    range: "100–140 BPM", music: "Hip-Hop" },
  { label: "Peak",      range: "140–170 BPM", music: "EDM Anthems" },
  { label: "Cool Down", range: "< 100 BPM",   music: "Chill R&B" },
];

type CardState = { status: "loading" } | { status: "ready"; track: TrackPick } | { status: "error" };

export default function AuraWorkout() {
  const [zoneIndex, setZoneIndex] = useState(2); // Peak, by default
  const zone = ZONES[zoneIndex];
  const [card, setCard] = useState<CardState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    setCard({ status: "loading" });
    api.catalog
      .experienceTrack({
        title: `Workout — ${zone.label}`,
        mood: zone.label,
        desc: `Workout intensity: ${zone.label} (${zone.range}). Music style: ${zone.music}.`,
      })
      .then((track) => {
        if (!cancelled) setCard({ status: "ready", track });
      })
      .catch(() => {
        if (!cancelled) setCard({ status: "error" });
      });
    return () => {
      cancelled = true;
    };
  }, [zoneIndex, zone.label, zone.range, zone.music]);

  return (
    <div className="aura-bg min-h-screen p-4 sm:p-6 lg:p-8 text-white">
      <AuroraBlobs />
      <div className="relative max-w-3xl mx-auto space-y-6">
        <div>
          <p className="text-white/40 text-[12px] uppercase tracking-widest mb-2 font-bold">Workout Mode</p>
          <h1 className="text-3xl sm:text-4xl font-black"><GradientText>Workout Coach</GradientText></h1>
          <p className="text-white/50 text-[14px] mt-2">A real track grounded to whichever intensity zone you pick.</p>
        </div>

        <div className="glass-card border-white/10 bg-white/[0.03] px-4 py-3 text-[12px] text-white/40">
          This app has no wearable/heart-rate integration, so the &quot;live BPM&quot; graph and
          calorie/duration stats that used to be here were invented and are gone. Pick a zone
          below instead — the track shown for it is real.
        </div>

        {/* Zone selector */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {ZONES.map((z, i) => (
            <button
              key={i}
              onClick={() => setZoneIndex(i)}
              className={`glass-card text-center py-4 transition-all ${i === zoneIndex ? "border-pink-500/50 bg-pink-500/10 scale-[1.03]" : "hover:border-white/20"}`}
            >
              <div className="text-[12px] font-black mb-1">{z.label}</div>
              <div className="text-[10px] text-white/40 mb-1">{z.range}</div>
              <div className="text-[10px] font-bold text-pink-400">{z.music}</div>
            </button>
          ))}
        </div>

        {/* Now playing — workout */}
        <GlassCard className="bg-gradient-to-r from-pink-500/10 to-purple-500/10 border-pink-500/20">
          <div className="text-[12px] text-pink-400 font-bold uppercase mb-3 flex items-center gap-1.5"><Music size={13} /> Matched to {zone.label}</div>
          <div className="flex items-center gap-4">
            {card.status === "loading" ? (
              <>
                <div className="w-14 h-14 rounded-2xl bg-white/5 animate-pulse shrink-0" />
                <div className="flex-1">
                  <div className="h-3 w-2/3 rounded bg-white/10 animate-pulse mb-2" />
                  <div className="h-2.5 w-1/2 rounded bg-white/5 animate-pulse" />
                </div>
              </>
            ) : card.status === "error" || !card.track ? (
              <>
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500 to-orange-500 flex items-center justify-center"><Dumbbell size={22} /></div>
                <div className="flex-1 text-[12px] text-white/30">Couldn&apos;t load a track right now.</div>
              </>
            ) : (
              <>
                {card.track.artwork_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={card.track.artwork_url} alt="" className="w-14 h-14 rounded-2xl object-cover shrink-0" />
                ) : (
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500 to-orange-500 flex items-center justify-center shrink-0"><Dumbbell size={22} /></div>
                )}
                <div className="flex-1 min-w-0">
                  <div className="text-[16px] font-black truncate">{card.track.track}</div>
                  <div className="text-[13px] text-white/50 truncate">
                    {card.track.artist}
                    {card.track.source && (
                      <span className={card.track.source === "spotify" ? "text-emerald-400" : "text-white/30"}> · {card.track.source}</span>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
          <p className="mt-3 text-[12px] text-white/50 flex items-start gap-1.5">
            <Bot size={13} className="shrink-0 mt-0.5" /> Pick a different zone above and Aura grounds a new real track to match it.
          </p>
        </GlassCard>
      </div>
    </div>
  );
}
