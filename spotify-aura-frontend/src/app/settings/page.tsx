"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Calendar, CloudSun, MapPin, Camera, Watch, Heart, Moon, NotebookPen, Mic,
  LogIn, Music, CheckCircle2, XCircle, Unlink, ArrowRight,
} from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import { AuraBadge } from "@/components/AuraBadge";
import { api, ApiResponseError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { SpotifyStatus } from "@/lib/types";

const PERMISSIONS = [
  { icon: Calendar,    key: "calendar",   label: "Calendar",    why: "Knows when you have meetings, appointments, or free time — music shifts accordingly." },
  { icon: CloudSun,    key: "weather",   label: "Weather",     why: "Rainy days shift your soundtrack to cozy; sunny mornings get energetic starts." },
  { icon: MapPin,      key: "location",  label: "Location",    why: "Commute, gym, home, café — each place has its own soundtrack context." },
  { icon: Camera,      key: "photos",    label: "Photos",      why: "Enriches your Life Chapters with visual memories alongside music." },
  { icon: Watch,       key: "wearables", label: "Wearables",   why: "Heart rate and activity data let Aura match BPM to your real-time body state." },
  { icon: Heart,       key: "heart",    label: "Heart Rate",  why: "Real-time energy calibration — workout music adapts as your heart rate climbs." },
  { icon: Moon,        key: "sleep",    label: "Sleep",       why: "Sleep quality data helps Aura choose gentler morning starts on poor sleep nights." },
  { icon: NotebookPen, key: "journal",  label: "Journal",     why: "Emotional context from your notes helps Aura choose music that truly resonates." },
  { icon: Mic,         key: "voice",   label: "Voice Notes", why: "Voice memos detect your mood through tone and integrate them into your chapters." },
];

function SettingsView() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [perms, setPerms] = useState<Record<string, boolean>>({
    calendar: true, weather: true, location: false, photos: false,
    wearables: true, heart: true, sleep: true, journal: false, voice: false,
  });

  const [spotifyStatus, setSpotifyStatus] = useState<SpotifyStatus | null>(null);
  const [spotifyStatusLoading, setSpotifyStatusLoading] = useState(true);
  const [spotifyBusy, setSpotifyBusy] = useState(false);
  const [spotifyError, setSpotifyError] = useState<string | null>(null);
  const [banner, setBanner] = useState<"connected" | "error" | null>(null);

  useEffect(() => {
    if (!user) {
      setSpotifyStatusLoading(false);
      return;
    }
    api.spotifyConnect.status().then(setSpotifyStatus).finally(() => setSpotifyStatusLoading(false));
  }, [user]);

  // Landing back from the Spotify OAuth redirect: the account was already
  // authenticated before the round trip (that's what /auth/spotify/login
  // required), so `user` doesn't need to be re-checked here — just refresh
  // the connection status so "Connected" replaces the stale "Connect" button
  // instead of flashing it, and clear the query param so a refresh doesn't
  // re-show the banner.
  useEffect(() => {
    const result = searchParams.get("spotify");
    if (result !== "connected" && result !== "error") return;
    setBanner(result);
    router.replace("/settings", { scroll: false });
    if (result === "connected") {
      setSpotifyStatusLoading(true);
      api.spotifyConnect.status().then(setSpotifyStatus).finally(() => setSpotifyStatusLoading(false));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  async function connectSpotify() {
    setSpotifyError(null);
    setSpotifyBusy(true);
    try {
      const { authorize_url } = await api.spotifyConnect.login();
      window.location.href = authorize_url;
    } catch (err) {
      setSpotifyError(
        err instanceof ApiResponseError
          ? err.message
          : "Couldn't start the Spotify connection. Try again."
      );
      setSpotifyBusy(false);
    }
  }

  async function disconnectSpotify() {
    setSpotifyBusy(true);
    try {
      await api.spotifyConnect.disconnect();
      setSpotifyStatus({ connected: false, display_name: null, spotify_user_id: null, connected_at: null });
    } catch {
      setSpotifyError("Couldn't disconnect right now. Try again.");
    } finally {
      setSpotifyBusy(false);
    }
  }

  return (
    <div className="aura-bg min-h-screen p-4 sm:p-6 lg:p-8 text-white">
      <AuroraBlobs />
      <div className="relative max-w-3xl mx-auto space-y-8">
        <div>
          <p className="text-white/40 text-[12px] uppercase tracking-widest mb-2 font-bold">Your Privacy</p>
          <h1 className="text-3xl sm:text-4xl font-black mb-2"><GradientText>Settings</GradientText></h1>
          <p className="text-white/50 text-[14px]">You are always in control. Every permission is optional — and every one improves your soundtrack.</p>
        </div>

        {banner === "connected" && (
          <div className="glass-card slide-up border-emerald-500/30 bg-emerald-500/10 px-4 py-3 flex items-center justify-between gap-3 flex-wrap">
            <div className="flex items-center gap-2.5 text-[13px] text-emerald-300 font-semibold">
              <CheckCircle2 size={16} className="shrink-0" /> Spotify connected — Dashboard, DNA, Insights, Memories, and Wrapped now use your real listening data.
            </div>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-emerald-500 text-black text-[12px] font-black hover:brightness-110 transition-all shrink-0"
            >
              View Dashboard <ArrowRight size={12} />
            </Link>
          </div>
        )}
        {banner === "error" && (
          <div className="glass-card slide-up border-red-500/30 bg-red-500/10 px-4 py-3 flex items-center gap-2.5 text-[13px] text-red-300 font-semibold">
            <XCircle size={16} className="shrink-0" /> Couldn&apos;t connect Spotify. If your app is in Development Mode, make sure your Spotify account is added under Dashboard → User Management, then try again.
          </div>
        )}

        {/* Real Spotify connection */}
        <GlassCard className="bg-gradient-to-r from-emerald-500/10 to-blue-500/10 border-emerald-500/20">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center shrink-0">
              <Music size={18} className="text-emerald-400" />
            </div>
            <div>
              <div className="text-[15px] font-black">Real Spotify Connection</div>
              <div className="text-[12px] text-white/50">Powers Dashboard, Music DNA, Life Chapters, Insights, Memories, and Wrapped with your actual listening data.</div>
            </div>
          </div>

          {!user ? (
            <p className="text-[13px] text-white/50">
              <Link href="/signin" className="text-emerald-400 font-semibold hover:text-emerald-300">Sign in</Link> to your Spotify Aura account first, then connect your real Spotify account here.
            </p>
          ) : spotifyStatusLoading ? (
            <div className="flex items-center gap-2.5 text-[13px] text-white/40">
              <div className="w-4 h-4 rounded-full border-2 border-white/15 border-t-emerald-400 animate-spin shrink-0" />
              Checking connection…
            </div>
          ) : spotifyStatus?.connected ? (
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div className="flex items-center gap-2">
                <AuraBadge color="green"><CheckCircle2 size={12} /> Connected</AuraBadge>
                <span className="text-[13px] text-white/70 font-semibold">{spotifyStatus.display_name ?? "Spotify account"}</span>
              </div>
              <button
                onClick={disconnectSpotify}
                disabled={spotifyBusy}
                className="px-3.5 py-2 rounded-full border border-white/15 text-white/70 text-[12px] font-bold hover:text-white hover:border-white/30 disabled:opacity-50 transition-colors inline-flex items-center gap-1.5"
              >
                <Unlink size={12} /> {spotifyBusy ? "Disconnecting…" : "Disconnect"}
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <button
                onClick={connectSpotify}
                disabled={spotifyBusy}
                className="px-4 py-2.5 rounded-full bg-[#1DB954] text-black text-[13px] font-black hover:brightness-110 disabled:opacity-50 transition-all inline-flex items-center gap-1.5"
              >
                <Music size={13} /> {spotifyBusy ? "Connecting…" : "Connect Spotify"}
              </button>
              {spotifyError && <p className="text-[12px] text-red-400">{spotifyError}</p>}
            </div>
          )}
        </GlassCard>

        {/* Data Sources */}
        <div>
          <h2 className="text-[16px] font-black mb-4">Data Sources & Permissions</h2>
          <div className="space-y-2">
            {PERMISSIONS.map(p => (
              <GlassCard key={p.key} className="py-3.5 px-4">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-white/5 flex items-center justify-center shrink-0">
                    <p.icon size={16} className="text-white/70" />
                  </div>
                  <div className="flex-1">
                    <div className="text-[14px] font-bold">{p.label}</div>
                    <div className="text-[12px] text-white/40 mt-0.5 leading-relaxed">{p.why}</div>
                  </div>
                  <button
                    onClick={() => setPerms(prev => ({ ...prev, [p.key]: !prev[p.key] }))}
                    role="switch"
                    aria-checked={perms[p.key]}
                    aria-label={`${perms[p.key] ? "Disable" : "Enable"} ${p.label}`}
                    className={`relative w-11 h-6 rounded-full transition-all duration-300 shrink-0 ${perms[p.key] ? "bg-emerald-500" : "bg-white/10"}`}
                  >
                    <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow-md transition-all duration-300 ${perms[p.key] ? "left-[22px]" : "left-0.5"}`} />
                  </button>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>

        {/* Profile */}
        <GlassCard>
          {loading ? (
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-white/5 animate-pulse shrink-0" />
              <div className="flex-1">
                <div className="h-3 w-32 rounded bg-white/10 animate-pulse mb-2" />
                <div className="h-2.5 w-40 rounded bg-white/5 animate-pulse" />
              </div>
            </div>
          ) : user ? (
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-emerald-400 to-blue-500 flex items-center justify-center text-[24px] font-black">
                {user.email[0]?.toUpperCase()}
              </div>
              <div>
                <div className="text-[16px] font-black">{user.email}</div>
                <div className="text-[12px] text-white/40">Signed in with Spotify Aura account</div>
                <AuraBadge color="green" className="mt-1">Aura Active</AuraBadge>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="text-[14px] font-bold">You&apos;re not signed in</div>
                <div className="text-[12px] text-white/40 mt-0.5">Sign in to sync your taste profile across devices.</div>
              </div>
              <Link
                href="/signin"
                className="px-4 py-2 rounded-full bg-emerald-500 text-black text-[12px] font-black hover:brightness-110 transition-all inline-flex items-center gap-1.5 shrink-0"
              >
                <LogIn size={12} /> Sign in
              </Link>
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  );
}

export default function AuraSettings() {
  return (
    <Suspense fallback={null}>
      <SettingsView />
    </Suspense>
  );
}
