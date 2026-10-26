"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Telescope, Guitar, Clock, Sparkles } from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, CartesianGrid,
} from "recharts";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { SpotifyOverview } from "@/lib/types";

const TOOLTIP_STYLE = { background: "#0f1115", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12, color: "#fff" };
const TIME_BUCKETS = [
  { label: "Night (12–5am)", test: (h: number) => h < 5 },
  { label: "Morning (5–11am)", test: (h: number) => h >= 5 && h < 11 },
  { label: "Afternoon (11am–5pm)", test: (h: number) => h >= 11 && h < 17 },
  { label: "Evening (5pm–12am)", test: (h: number) => h >= 17 },
];
const POPULARITY_BUCKETS = [
  { label: "Niche (0–33)", test: (p: number) => p < 34, color: "#3B82F6" },
  { label: "Emerging (34–66)", test: (p: number) => p >= 34 && p < 67, color: "#8B5CF6" },
  { label: "Mainstream (67–100)", test: (p: number) => p >= 67, color: "#1DB954" },
];

export default function AuraInsights() {
  const { user } = useAuth();
  const [overview, setOverview] = useState<SpotifyOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }
    api.spotifyConnect.overview().then(setOverview).finally(() => setLoading(false));
  }, [user]);

  const connected = overview?.connected ?? false;

  const listeningTimes = useMemo(() => {
    const counts = TIME_BUCKETS.map((b) => ({ label: b.label, count: 0 }));
    for (const t of overview?.recently_played ?? []) {
      if (!t.played_at) continue;
      const hour = new Date(t.played_at).getHours();
      const i = TIME_BUCKETS.findIndex((b) => b.test(hour));
      if (i >= 0) counts[i].count += 1;
    }
    return counts;
  }, [overview]);

  const popularityMix = useMemo(() => {
    const counts = POPULARITY_BUCKETS.map((b) => ({ name: b.label, value: 0, color: b.color }));
    for (const a of overview?.top_artists ?? []) {
      if (a.popularity == null) continue;
      const i = POPULARITY_BUCKETS.findIndex((b) => b.test(a.popularity!));
      if (i >= 0) counts[i].value += 1;
    }
    return counts.filter((c) => c.value > 0);
  }, [overview]);

  const distinctGenres = new Set(overview?.top_artists?.flatMap((a) => a.genres) ?? []).size;
  const distinctArtistsRecent = new Set(overview?.recently_played?.map((t) => t.artist) ?? []).size;
  const hasListeningTimes = listeningTimes.some((b) => b.count > 0);

  return (
    <div className="aura-bg min-h-screen p-4 sm:p-6 lg:p-8 text-white">
      <AuroraBlobs />
      <div className="relative w-full space-y-6">
        <div>
          <p className="text-white/40 text-[12px] uppercase tracking-widest mb-2 font-bold">Your Music Intelligence</p>
          <h1 className="text-3xl sm:text-4xl font-black"><GradientText>Personal Insights</GradientText></h1>
          <p className="text-white/50 text-[14px] mt-2">Built entirely from your real Spotify data.</p>
        </div>

        {!user ? (
          <GlassCard className="text-center py-16">
            <Sparkles size={36} className="text-white/20 mx-auto mb-4" />
            <p className="text-white/50 text-[14px] mb-4">Sign in and connect Spotify to see your real insights.</p>
            <Link href="/signin" className="inline-flex px-5 py-2.5 rounded-full bg-emerald-500 text-black text-[13px] font-black hover:brightness-110 transition-all">Sign in</Link>
          </GlassCard>
        ) : loading ? (
          <GlassCard className="text-center py-16">
            <div className="w-8 h-8 rounded-full border-2 border-white/10 border-t-emerald-400 animate-spin mx-auto" />
          </GlassCard>
        ) : !connected ? (
          <GlassCard className="text-center py-16">
            <Sparkles size={36} className="text-white/20 mx-auto mb-4" />
            <p className="text-white/50 text-[14px] mb-4">Connect Spotify for a real breakdown of your genres, listening times, and taste.</p>
            <Link href="/settings" className="inline-flex px-5 py-2.5 rounded-full bg-emerald-500 text-black text-[13px] font-black hover:brightness-110 transition-all">Connect Spotify</Link>
          </GlassCard>
        ) : (
          <>
            {/* Real KPI row */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {[
                { label: "Genres in Top Artists", value: distinctGenres, icon: Guitar, color: "#3B82F6" },
                { label: "Distinct Recent Artists", value: distinctArtistsRecent, icon: Telescope, color: "#8B5CF6" },
                { label: "Recent Plays Tracked", value: overview?.recently_played?.length ?? 0, icon: Clock, color: "#1DB954" },
              ].map((k) => (
                <GlassCard key={k.label} className="text-center py-5">
                  <div className="flex justify-center mb-2"><k.icon size={22} style={{ color: k.color }} /></div>
                  <div className="text-2xl font-black" style={{ color: k.color }}>{k.value}</div>
                  <div className="text-[11px] text-white/50 mt-1 font-semibold">{k.label}</div>
                </GlassCard>
              ))}
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
              {/* Real listening-time distribution, from actual played_at timestamps */}
              <GlassCard>
                <div className="text-[13px] font-bold text-white/60 mb-4">When You Actually Listen <span className="text-white/30 font-normal">(from recent plays)</span></div>
                {hasListeningTimes ? (
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={listeningTimes}>
                      <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
                      <XAxis dataKey="label" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 10 }} axisLine={false} tickLine={false} />
                      <YAxis allowDecimals={false} tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={TOOLTIP_STYLE} />
                      <Bar dataKey="count" radius={[6, 6, 0, 0]} fill="#1DB954" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-[13px] text-white/40 py-8 text-center">Not enough recent plays yet to show a pattern.</p>
                )}
              </GlassCard>

              {/* Real popularity mix of top artists */}
              <GlassCard className="flex flex-col">
                <div className="text-[13px] font-bold text-white/60 mb-4">Mainstream vs. Niche <span className="text-white/30 font-normal">(your top artists&apos; real Spotify popularity)</span></div>
                {popularityMix.length > 0 ? (
                  <div className="flex items-center gap-4 flex-1">
                    <ResponsiveContainer width={130} height={130}>
                      <PieChart>
                        <Pie data={popularityMix} cx="50%" cy="50%" innerRadius={38} outerRadius={60} paddingAngle={3} dataKey="value">
                          {popularityMix.map((e, i) => <Cell key={i} fill={e.color} />)}
                        </Pie>
                        <Tooltip contentStyle={TOOLTIP_STYLE} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="space-y-1.5 flex-1">
                      {popularityMix.map((m) => (
                        <div key={m.name} className="flex items-center justify-between">
                          <div className="flex items-center gap-1.5">
                            <div className="w-2 h-2 rounded-full" style={{ background: m.color }} />
                            <span className="text-[12px] text-white/60">{m.name}</span>
                          </div>
                          <span className="text-[12px] font-bold" style={{ color: m.color }}>{m.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-[13px] text-white/40 py-8 text-center">No top artist popularity data yet.</p>
                )}
              </GlassCard>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
