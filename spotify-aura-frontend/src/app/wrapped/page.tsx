"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Music, Crown, Music2, ArrowLeft, ArrowRight, Sparkles } from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import { AuraBadge } from "@/components/AuraBadge";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { SpotifyOverview } from "@/lib/types";

interface Slide {
  id: string;
  bg: string;
  content: React.ReactNode;
}

const HERO_SLIDE: Slide = {
  id: "hero",
  bg: "from-emerald-900/80 to-black",
  content: (
    <div className="text-center">
      <div className="flex justify-center mb-6"><Music size={56} /></div>
      <p className="text-white/50 text-[14px] uppercase tracking-widest mb-3">Your Real Music Wrapped</p>
      <h1 className="text-5xl font-black leading-tight mb-4">
        <span className="gradient-text">Aura Wrapped</span>
      </h1>
      <p className="text-white/50">Built entirely from your real Spotify data — nothing simulated.</p>
    </div>
  ),
};

function realSlides(overview: SpotifyOverview): Slide[] {
  const slides: Slide[] = [];
  const topArtist = overview.top_artists[0];
  const topTrack = overview.top_tracks[0];

  if (topArtist) {
    slides.push({
      id: "real-top-artist",
      bg: "from-pink-900/80 to-black",
      content: (
        <div className="text-center">
          <p className="text-white/50 uppercase tracking-widest text-[13px] mb-6">Your real #1 artist</p>
          <div className="flex justify-center mb-4">
            {topArtist.image_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={topArtist.image_url} alt="" className="w-28 h-28 rounded-full object-cover" />
            ) : (
              <Crown size={56} className="text-pink-400" />
            )}
          </div>
          <div className="text-4xl font-black text-pink-400 mb-2">{topArtist.name}</div>
          {topArtist.genres.length > 0 && (
            <p className="text-white/50 mb-4">{topArtist.genres.slice(0, 3).join(" · ")}</p>
          )}
          {topArtist.external_url && (
            <a href={topArtist.external_url} target="_blank" rel="noreferrer" className="text-emerald-400 text-[13px] font-bold hover:text-emerald-300">
              Open on Spotify →
            </a>
          )}
        </div>
      ),
    });
  }

  if (topTrack) {
    slides.push({
      id: "real-top-track",
      bg: "from-blue-900/80 to-black",
      content: (
        <div className="text-center">
          <p className="text-white/50 uppercase tracking-widest text-[13px] mb-6">Your real #1 track</p>
          <div className="flex justify-center mb-4">
            {topTrack.album_image ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={topTrack.album_image} alt="" className="w-28 h-28 rounded-2xl object-cover" />
            ) : (
              <Music2 size={56} className="text-blue-400" />
            )}
          </div>
          <div className="text-3xl font-black text-blue-400 mb-1">{topTrack.name}</div>
          <p className="text-white/50 mb-4">{topTrack.artist}</p>
          {topTrack.external_url && (
            <a href={topTrack.external_url} target="_blank" rel="noreferrer" className="text-emerald-400 text-[13px] font-bold hover:text-emerald-300">
              Open on Spotify →
            </a>
          )}
        </div>
      ),
    });
  }

  if (overview.top_genres.length > 0) {
    slides.push({
      id: "real-genres",
      bg: "from-purple-900/80 to-black",
      content: (
        <div className="text-center">
          <p className="text-white/50 uppercase tracking-widest text-[13px] mb-6">Your real top genres</p>
          <div className="flex flex-wrap gap-2 justify-center max-w-sm mx-auto">
            {overview.top_genres.map((g) => (
              <AuraBadge key={g} color="green">{g}</AuraBadge>
            ))}
          </div>
        </div>
      ),
    });
  }

  const distinctGenres = new Set(overview.top_artists.flatMap((a) => a.genres)).size;
  slides.push({
    id: "real-summary",
    bg: "from-emerald-900/80 to-purple-900/80",
    content: (
      <div className="text-center">
        <p className="text-white/50 uppercase tracking-widest text-[13px] mb-4">Your Real Numbers</p>
        <div className="grid grid-cols-2 gap-3 max-w-sm mx-auto">
          {[
            [String(overview.top_artists.length), "Top Artists Tracked"],
            [String(overview.top_tracks.length), "Top Tracks Tracked"],
            [String(distinctGenres), "Genres in Top Artists"],
            [String(overview.recently_played.length), "Recent Plays Tracked"],
          ].map(([v, l]) => (
            <GlassCard key={l} className="py-4 text-center">
              <div className="text-2xl font-black text-emerald-400">{v}</div>
              <div className="text-[11px] text-white/50 mt-1">{l}</div>
            </GlassCard>
          ))}
        </div>
      </div>
    ),
  });

  return slides;
}

export default function AuraWrapped() {
  const { user } = useAuth();
  const [slide, setSlide] = useState(0);
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
  const slides: Slide[] = connected && overview ? [HERO_SLIDE, ...realSlides(overview)] : [HERO_SLIDE];
  const current = slides[slide] ?? slides[0];

  return (
    <div className={`aura-bg min-h-screen bg-gradient-to-b ${current.bg} transition-all duration-700 flex flex-col items-center justify-center p-4 sm:p-6 text-white relative`}>
      <AuroraBlobs />
      <div className="relative w-full max-w-lg">
        {!user ? (
          <GlassCard className="text-center py-12 mb-8">
            <Sparkles size={32} className="text-white/20 mx-auto mb-4" />
            <p className="text-white/50 text-[14px] mb-4">Sign in and connect Spotify to see your real Wrapped.</p>
            <Link href="/signin" className="inline-flex px-5 py-2.5 rounded-full bg-emerald-500 text-black text-[13px] font-black hover:brightness-110 transition-all">Sign in</Link>
          </GlassCard>
        ) : loading ? (
          <GlassCard className="text-center py-12 mb-8">
            <div className="w-8 h-8 rounded-full border-2 border-white/10 border-t-emerald-400 animate-spin mx-auto" />
          </GlassCard>
        ) : !connected ? (
          <GlassCard className="text-center py-12 mb-8">
            <Sparkles size={32} className="text-white/20 mx-auto mb-4" />
            <p className="text-white/50 text-[14px] mb-4">Connect Spotify to build your real Wrapped — top artist, top track, and top genres.</p>
            <Link href="/settings" className="inline-flex px-5 py-2.5 rounded-full bg-emerald-500 text-black text-[13px] font-black hover:brightness-110 transition-all">Connect Spotify</Link>
          </GlassCard>
        ) : (
          <>
            {/* Slide indicators */}
            <div className="flex gap-1.5 mb-12 justify-center">
              {slides.map((s, i) => (
                <button
                  key={i}
                  onClick={() => setSlide(i)}
                  aria-label={`Go to slide ${i + 1} of ${slides.length}: ${s.id}`}
                  aria-current={i === slide}
                  className={`h-1 rounded-full transition-all duration-300 ${i === slide ? "w-8 bg-white" : "w-3 bg-white/20"}`}
                />
              ))}
            </div>

            {/* Slide content */}
            <div className="slide-up" key={slide}>
              {current.content}
            </div>

            {/* Nav buttons */}
            <div className="flex gap-3 mt-12">
              {slide > 0 && (
                <button onClick={() => setSlide(s => s - 1)} className="flex-1 py-3 rounded-xl glass-card text-white/60 font-bold text-[14px] hover:text-white transition-colors flex items-center justify-center gap-1.5">
                  <ArrowLeft size={14} /> Back
                </button>
              )}
              {slide < slides.length - 1 && (
                <button onClick={() => setSlide(s => s + 1)} className="flex-1 py-3 rounded-xl bg-white text-black font-black text-[14px] hover:brightness-90 transition-all flex items-center justify-center gap-1.5">
                  Next <ArrowRight size={14} />
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
