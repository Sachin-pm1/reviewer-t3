"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Music2, Sparkles, Users, Guitar } from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { SpotifyOverview } from "@/lib/types";

function average(values: (number | null)[]): number | null {
  const nums = values.filter((v): v is number => v != null);
  if (nums.length === 0) return null;
  return Math.round(nums.reduce((a, b) => a + b, 0) / nums.length);
}

export default function AuraDNA() {
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

  const genreCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const artist of overview?.top_artists ?? []) {
      for (const genre of artist.genres) counts[genre] = (counts[genre] ?? 0) + 1;
    }
    return Object.entries(counts)
      .map(([genre, count]) => ({ genre, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8);
  }, [overview]);

  const avgArtistPopularity = average(overview?.top_artists?.map((a) => a.popularity) ?? []);
  const avgTrackPopularity = average(overview?.top_tracks?.map((t) => t.popularity) ?? []);
  const totalGenres = new Set(overview?.top_artists?.flatMap((a) => a.genres) ?? []).size;

  return (
    <div className="aura-bg min-h-screen p-4 sm:p-6 lg:p-8 text-white">
      <AuroraBlobs />
      <div className="relative w-full space-y-8">
        <div>
          <p className="text-white/40 text-[12px] uppercase tracking-widest mb-2 font-bold">Your Musical Identity</p>
          <h1 className="text-3xl sm:text-4xl font-black"><GradientText>Music DNA</GradientText></h1>
          <p className="text-white/50 text-[14px] mt-2">Built entirely from your real Spotify data — no simulated traits.</p>
        </div>

        {!user ? (
          <GlassCard className="text-center py-16">
            <Sparkles size={36} className="text-white/20 mx-auto mb-4" />
            <p className="text-white/50 text-[14px] mb-4">Sign in and connect Spotify to see your real Music DNA.</p>
            <Link href="/signin" className="inline-flex px-5 py-2.5 rounded-full bg-emerald-500 text-black text-[13px] font-black hover:brightness-110 transition-all">
              Sign in
            </Link>
          </GlassCard>
        ) : loading ? (
          <GlassCard className="text-center py-16">
            <div className="w-8 h-8 rounded-full border-2 border-white/10 border-t-emerald-400 animate-spin mx-auto" />
          </GlassCard>
        ) : !connected ? (
          <GlassCard className="text-center py-16">
            <Sparkles size={36} className="text-white/20 mx-auto mb-4" />
            <p className="text-white/50 text-[14px] mb-4">Connect Spotify to see your real top genres, artists, and tracks here.</p>
            <Link href="/settings" className="inline-flex px-5 py-2.5 rounded-full bg-emerald-500 text-black text-[13px] font-black hover:brightness-110 transition-all">
              Connect Spotify
            </Link>
          </GlassCard>
        ) : genreCounts.length === 0 && (overview?.top_artists?.length ?? 0) === 0 ? (
          <GlassCard className="text-center py-16 text-white/40 text-[14px]">
            Not enough listening data on your Spotify account yet to build a profile.
          </GlassCard>
        ) : (
          <>
            {/* Real metrics — every number here comes directly from Spotify */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: "Genres in Your Top Artists", value: String(totalGenres), unit: "", icon: Guitar, color: "#1DB954" },
                { label: "Avg. Artist Popularity", value: avgArtistPopularity != null ? String(avgArtistPopularity) : "—", unit: "/100", icon: Users, color: "#8B5CF6" },
                { label: "Avg. Track Popularity", value: avgTrackPopularity != null ? String(avgTrackPopularity) : "—", unit: "/100", icon: Music2, color: "#3B82F6" },
                { label: "Top Artists Tracked", value: String(overview?.top_artists?.length ?? 0), unit: "", icon: Sparkles, color: "#F59E0B" },
              ].map((m) => (
                <GlassCard key={m.label} className="text-center py-6">
                  <div className="flex justify-center mb-2"><m.icon size={22} style={{ color: m.color }} /></div>
                  <div className="text-2xl font-black" style={{ color: m.color }}>{m.value}<span className="text-[13px] text-white/40">{m.unit}</span></div>
                  <div className="text-[11px] text-white/50 mt-1 font-semibold">{m.label}</div>
                </GlassCard>
              ))}
            </div>
            <p className="text-[11px] text-white/30 -mt-4">Popularity is Spotify&apos;s own 0–100 score for how mainstream an artist/track is right now — higher isn&apos;t &quot;better&quot;, just more widely streamed.</p>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Real genre distribution */}
              <GlassCard>
                <div className="text-[13px] font-bold text-white/60 mb-4">Your Genres, by How Many Top Artists Share Them</div>
                {genreCounts.length > 0 ? (
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={genreCounts} layout="vertical" margin={{ left: 12 }}>
                      <CartesianGrid stroke="rgba(255,255,255,0.05)" horizontal={false} />
                      <XAxis type="number" allowDecimals={false} tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis type="category" dataKey="genre" width={110} tick={{ fill: "rgba(255,255,255,0.6)", fontSize: 11 }} axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={{ background: "#1e222b", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, fontSize: 12 }} />
                      <Bar dataKey="count" fill="#1DB954" radius={[0, 6, 6, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <p className="text-[13px] text-white/40 py-8 text-center">Spotify didn&apos;t return genre data for your top artists.</p>
                )}
              </GlassCard>

              {/* Real top artists */}
              <GlassCard>
                <div className="text-[13px] font-bold text-white/60 mb-4">Your Real Top Artists</div>
                <div className="space-y-2.5">
                  {(overview?.top_artists ?? []).slice(0, 8).map((a) => (
                    <a
                      key={a.name}
                      href={a.external_url ?? "#"}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-2.5 hover:bg-white/5 rounded-lg px-2 -mx-2 py-1 transition-colors"
                    >
                      {a.image_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={a.image_url} alt="" className="w-8 h-8 rounded-full object-cover shrink-0" />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center shrink-0"><Music2 size={12} className="text-white/40" /></div>
                      )}
                      <div className="min-w-0 flex-1">
                        <div className="text-[13px] font-semibold truncate">{a.name}</div>
                        {a.genres.length > 0 && <div className="text-[10px] text-white/35 truncate">{a.genres.slice(0, 2).join(" · ")}</div>}
                      </div>
                      {a.popularity != null && <span className="text-[11px] text-white/40 shrink-0">{a.popularity}</span>}
                    </a>
                  ))}
                </div>
              </GlassCard>
            </div>

            {/* Real top tracks */}
            <GlassCard>
              <div className="text-[13px] font-bold text-white/60 mb-4">Your Real Top Tracks</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {(overview?.top_tracks ?? []).slice(0, 10).map((t, i) => (
                  <a
                    key={i}
                    href={t.external_url ?? "#"}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-2.5 hover:bg-white/5 rounded-lg px-2 -mx-2 py-1.5 transition-colors"
                  >
                    {t.album_image ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={t.album_image} alt="" className="w-8 h-8 rounded-lg object-cover shrink-0" />
                    ) : (
                      <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center shrink-0"><Music2 size={12} className="text-white/40" /></div>
                    )}
                    <div className="min-w-0 flex-1">
                      <div className="text-[13px] font-semibold truncate">{t.name}</div>
                      <div className="text-[10px] text-white/35 truncate">{t.artist}</div>
                    </div>
                  </a>
                ))}
              </div>
            </GlassCard>
          </>
        )}
      </div>
    </div>
  );
}
