"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Sparkles, Play, ArrowRight, Music2 } from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import { AuraBadge } from "@/components/AuraBadge";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { SpotifyOverview } from "@/lib/types";

export default function AuraDashboard() {
  const { user } = useAuth();
  const [overview, setOverview] = useState<SpotifyOverview | null>(null);

  useEffect(() => {
    if (!user) return;
    api.spotifyConnect.overview().then(setOverview).catch(() => {});
  }, [user]);

  const connected = overview?.connected ?? false;
  const greetingName = overview?.display_name ?? user?.email.split("@")[0] ?? "there";
  const topTrack = overview?.top_tracks?.[0];
  const today = new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" });

  return (
    <div className="aura-bg min-h-screen p-4 sm:p-6 lg:p-8 text-white">
      <AuroraBlobs />
      <div className="relative w-full space-y-6">

        {/* Header */}
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-white/40 text-[13px] font-medium mb-1">{today}</div>
            <h1 className="text-2xl sm:text-3xl font-black">
              Good to see you, <GradientText>{greetingName}.</GradientText>
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <AuraBadge color="green">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /> {connected ? "Spotify Connected" : "Not Connected"}
            </AuraBadge>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-emerald-400 to-blue-500 flex items-center justify-center text-[16px] font-black shrink-0">
              {greetingName[0]?.toUpperCase()}
            </div>
          </div>
        </div>

        {!connected && (
          <div className="glass-card border-emerald-500/20 bg-emerald-500/5 px-4 py-3 flex items-center justify-between gap-3 flex-wrap text-[13px]">
            <span className="text-white/60">Connect your real Spotify account to power this dashboard with your actual listening data.</span>
            <Link href="/settings" className="text-emerald-400 font-bold hover:text-emerald-300 shrink-0">Connect Spotify →</Link>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recently played — main column, real data only */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-[16px] font-black">Recently Played</h2>
              <Link href="/memories" className="text-[12px] text-emerald-400 font-bold hover:text-emerald-300 flex items-center gap-1">
                Full view <ArrowRight size={12} />
              </Link>
            </div>
            {connected && (overview?.recently_played?.length ?? 0) > 0 ? (
              <div className="space-y-2">
                {overview!.recently_played.slice(0, 7).map((t, i) => (
                  <GlassCard key={i} className="flex items-center gap-4 py-3 px-4">
                    {t.album_image ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={t.album_image} alt="" className="w-9 h-9 rounded-lg object-cover shrink-0" />
                    ) : (
                      <div className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center shrink-0"><Music2 size={16} className="text-white/40" /></div>
                    )}
                    <div className="flex-1 min-w-0">
                      <span className="text-[13px] font-bold truncate block">{t.name}</span>
                      <div className="text-[11px] text-white/40 truncate">{t.artist}</div>
                    </div>
                    <span className="text-[11px] text-white/30 shrink-0">
                      {t.played_at ? new Date(t.played_at).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" }) : ""}
                    </span>
                  </GlassCard>
                ))}
              </div>
            ) : (
              <GlassCard className="text-center py-12 text-[13px] text-white/40">
                {connected ? "No recent plays yet — play something on Spotify and check back." : "Connect Spotify to see what you've actually been listening to."}
              </GlassCard>
            )}
          </div>

          {/* Right column */}
          <div className="space-y-5">
            {/* Top Genres snapshot */}
            <GlassCard>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-[13px] font-black">Top Genres</h2>
                <Link href="/dna" className="text-[11px] text-emerald-400 flex items-center gap-1">Full DNA <ArrowRight size={11} /></Link>
              </div>
              {connected && (overview?.top_genres?.length ?? 0) > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {overview!.top_genres.slice(0, 6).map((g) => (
                    <AuraBadge key={g} color="green">{g}</AuraBadge>
                  ))}
                </div>
              ) : (
                <p className="text-[12px] text-white/40">{connected ? "No genre data yet." : "Connect Spotify to see your real genres."}</p>
              )}
            </GlassCard>

            {/* Top track — real data only */}
            <GlassCard className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/20">
              <div className="text-[11px] text-purple-400 font-bold uppercase tracking-wider mb-2 flex items-center gap-1">
                <Sparkles size={12} /> Your Top Track Right Now
              </div>
              {connected && topTrack ? (
                <>
                  <div className="flex items-center gap-3 mb-3">
                    {topTrack.album_image ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={topTrack.album_image} alt="" className="w-11 h-11 rounded-xl object-cover shrink-0" />
                    ) : (
                      <div className="w-11 h-11 rounded-xl bg-white/5 flex items-center justify-center shrink-0"><Music2 size={18} className="text-white/40" /></div>
                    )}
                    <div className="min-w-0">
                      <div className="text-[14px] font-black truncate">{topTrack.name}</div>
                      <div className="text-[12px] text-white/50 truncate">{topTrack.artist}</div>
                    </div>
                  </div>
                  <a
                    href={topTrack.external_url ?? "#"}
                    target="_blank"
                    rel="noreferrer"
                    className="w-full py-2 rounded-xl bg-purple-500/20 text-purple-300 text-[12px] font-bold hover:bg-purple-500/30 transition-colors flex items-center justify-center gap-1.5"
                  >
                    <Play size={12} className="fill-current" /> Open in Spotify
                  </a>
                </>
              ) : (
                <p className="text-[12px] text-white/40">{connected ? "No top track yet." : "Connect Spotify to see your real top track."}</p>
              )}
            </GlassCard>
          </div>
        </div>
      </div>
    </div>
  );
}
