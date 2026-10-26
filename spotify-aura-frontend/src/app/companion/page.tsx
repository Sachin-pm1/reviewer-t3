"use client";

import { Suspense, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Sparkles, Headphones, Bot, Settings, Play, Pause, ArrowRight, Music2 } from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import { AuraBadge } from "@/components/AuraBadge";
import { api, ApiResponseError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useAudioPlayer, type PlayerTrack } from "@/lib/audio-player-context";
import type { CompanionTurn, Journey, TasteProfile, TrackPick } from "@/lib/types";

const SUGGESTIONS = [
  "Surprise me — I'm bored of my own playlists.",
  "I'm feeling anxious.",
  "I need motivation.",
  "I'm going on a road trip.",
  "I want deep focus.",
  "Something like my usual taste, but not the same songs.",
];

const TASTE_KEY = "spotify-aura-taste-profile";

interface Message {
  role: "user" | "aura";
  text: string;
  journey?: Journey;
}

function loadTaste(): TasteProfile | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(TASTE_KEY);
    return raw ? (JSON.parse(raw) as TasteProfile) : null;
  } catch {
    return null;
  }
}

function CompanionView() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const handedOffPrompt = useRef(false);
  const { user, loading: authLoading } = useAuth();

  const [taste, setTaste] = useState<TasteProfile | null>(null);
  const [tasteReady, setTasteReady] = useState(false);
  const [artistsInput, setArtistsInput] = useState("");
  const [genresInput, setGenresInput] = useState("");
  const [novelty, setNovelty] = useState(60);

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const { current: nowPlaying, playing, playQueue, toggle } = useAudioPlayer();

  // Signed-in listeners get their taste profile from the account (follows
  // them across devices); signed-out falls back to this browser's localStorage.
  useEffect(() => {
    if (authLoading) return;
    if (user) {
      api.me
        .getTaste()
        .then((saved) => {
          setTaste(saved);
          setNovelty(saved.novelty);
          setTasteReady(true);
        })
        .catch(() => {
          // No saved profile yet (or a transient error) — fall through to setup.
        });
      return;
    }
    const saved = loadTaste();
    if (saved) {
      setTaste(saved);
      setNovelty(saved.novelty);
      setTasteReady(true);
    }
  }, [user, authLoading]);

  // A prompt handed off from another page (e.g. Discovery's "Begin Experience")
  // arrives as ?prompt=... — send it once taste is ready, then drop it from
  // the URL so refreshing the page doesn't resend it.
  useEffect(() => {
    const prompt = searchParams.get("prompt");
    if (!prompt || !tasteReady || handedOffPrompt.current) return;
    handedOffPrompt.current = true;
    router.replace("/companion");
    send(prompt);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tasteReady, searchParams]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function startTaste() {
    const profile: TasteProfile = {
      seed_artists: artistsInput.split(",").map((s) => s.trim()).filter(Boolean).slice(0, 10),
      seed_genres: genresInput.split(",").map((s) => s.trim()).filter(Boolean).slice(0, 10),
      novelty,
    };
    // Always cache locally too (instant, and a fallback if the save below fails).
    window.localStorage.setItem(TASTE_KEY, JSON.stringify(profile));
    setTaste(profile);
    setTasteReady(true);
    if (user) {
      api.me.setTaste(profile).catch(() => {
        // Local state + cache already updated — a failed sync isn't fatal here.
      });
    }
  }

  function toPlayerTrack(id: string, p: TrackPick): PlayerTrack | null {
    if (!p.preview_url) return null;
    return { id, name: p.track, artist: p.artist, artworkUrl: p.artwork_url, previewUrl: p.preview_url, externalUrl: p.external_url };
  }

  function playPick(journey: Journey, pickIndex: number) {
    const id = `${journey.picks[pickIndex].artist}-${journey.picks[pickIndex].track}-${pickIndex}`;
    if (nowPlaying?.id === id) {
      toggle();
      return;
    }
    const playable = journey.picks
      .map((p, i) => toPlayerTrack(`${p.artist}-${p.track}-${i}`, p))
      .filter((t): t is PlayerTrack => t !== null);
    const startIndex = playable.findIndex((t) => t.id === id);
    if (startIndex >= 0) playQueue(playable, startIndex);
  }

  async function send(text: string) {
    if (!text.trim() || !taste) return;
    const history: CompanionTurn[] = messages.map((m) => ({ role: m.role, text: m.text }));
    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.companion.chat(text, history, taste);
      setMessages((m) => [...m, { role: "aura", text: res.reply, journey: res.journey ?? undefined }]);
    } catch (err) {
      const message =
        err instanceof ApiResponseError && err.status === 503
          ? "Aura's AI backend isn't configured on this deployment yet — set ANTHROPIC_API_KEY on the API and reload."
          : "Something went sideways reaching Aura. Try again in a moment.";
      setMessages((m) => [...m, { role: "aura", text: message }]);
    } finally {
      setLoading(false);
    }
  }

  if (!tasteReady) {
    return (
      <div className="aura-bg min-h-screen flex items-center justify-center p-4 sm:p-6 text-white">
        <AuroraBlobs />
        <div className="relative w-full max-w-md">
          <div className="text-center mb-6">
            <p className="text-white/40 text-[12px] uppercase tracking-widest mb-2 font-bold">
              Before we start
            </p>
            <h1 className="text-3xl font-black mb-2">
              <GradientText>Tell Aura your taste.</GradientText>
            </h1>
            <p className="text-white/50 text-[13px]">
              So it knows exactly what &quot;new&quot; means for you — and can prove every pick
              is a deliberate stretch, not a guess.
            </p>
          </div>
          <GlassCard className="space-y-4">
            <div>
              <label className="text-[11px] text-white/50 font-bold uppercase tracking-wide">
                Artists you already love
              </label>
              <input
                value={artistsInput}
                onChange={(e) => setArtistsInput(e.target.value)}
                placeholder="Tame Impala, Arijit Singh, Daft Punk…"
                className="mt-1.5 w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-[13px] placeholder:text-white/25 focus:outline-none focus:border-emerald-500/50"
              />
            </div>
            <div>
              <label className="text-[11px] text-white/50 font-bold uppercase tracking-wide">
                Genres you gravitate to
              </label>
              <input
                value={genresInput}
                onChange={(e) => setGenresInput(e.target.value)}
                placeholder="indie rock, lo-fi, bollywood…"
                className="mt-1.5 w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-[13px] placeholder:text-white/25 focus:outline-none focus:border-emerald-500/50"
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-[11px] text-white/50 font-bold uppercase tracking-wide">
                  Novelty dial
                </label>
                <span className="text-[12px] font-black text-emerald-400">{novelty}/100</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={novelty}
                onChange={(e) => setNovelty(Number(e.target.value))}
                className="w-full accent-emerald-500"
              />
              <div className="flex justify-between text-[10px] text-white/30 mt-1">
                <span>Stay close to my taste</span>
                <span>Push me hard</span>
              </div>
            </div>
            <button
              onClick={startTaste}
              className="w-full py-3 rounded-xl bg-emerald-500 text-black font-black text-[14px] hover:brightness-110 transition-all flex items-center justify-center gap-1.5"
            >
              Start discovering <Sparkles size={14} />
            </button>
          </GlassCard>
        </div>
      </div>
    );
  }

  return (
    <div className="aura-bg min-h-screen flex flex-col text-white">
      <AuroraBlobs />
      <div className="relative flex-1 flex flex-col max-w-3xl mx-auto w-full p-4 sm:p-6">
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-black mb-1">
              <GradientText>Aura Companion</GradientText>
            </h1>
            <p className="text-white/40 text-[13px]">
              Tell me what you&apos;re after — I&apos;ll deliberately stretch past your usual rotation.
            </p>
          </div>
          <button
            onClick={() => setTasteReady(false)}
            className="shrink-0 glass-card px-3 py-2 text-[11px] text-white/50 hover:text-white transition-colors flex items-center gap-1.5"
          >
            <Settings size={12} /> Novelty {taste?.novelty}/100
          </button>
        </div>

        {/* Chat log */}
        <div className="flex-1 overflow-y-auto space-y-4 pb-4 min-h-[300px]">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="flex justify-center mb-4"><Headphones size={40} className="text-white/30" /></div>
              <p className="text-white/40 text-[14px] mb-6">What are you feeling right now?</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="glass-card px-4 py-2 text-[13px] text-white/70 hover:text-white hover:border-white/20 transition-all"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              {m.role === "aura" && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-blue-500 flex items-center justify-center shrink-0">
                  <Bot size={16} className="text-black" />
                </div>
              )}
              <div className={`max-w-[80%] space-y-3 ${m.role === "user" ? "items-end" : "items-start"} flex flex-col`}>
                <div
                  className={`rounded-2xl px-4 py-3 text-[14px] leading-relaxed ${
                    m.role === "user" ? "bg-emerald-500 text-black font-semibold" : "glass-card text-white/90"
                  }`}
                >
                  {m.text}
                </div>
                {m.journey && (
                  <GlassCard className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 border-purple-500/20 w-full slide-up">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-[11px] text-purple-400 font-bold uppercase tracking-wider flex items-center gap-1">
                        <Sparkles size={11} /> Your Listening Journey
                      </div>
                      <AuraBadge color="purple">{m.journey.mood}</AuraBadge>
                    </div>
                    <p className="text-[12px] text-white/50 mb-3 leading-relaxed">{m.journey.reasoning}</p>
                    <div className="mb-3">
                      <div className="text-[10px] text-white/40 mb-1">Energy</div>
                      <div className="w-full h-1.5 bg-white/10 rounded-full">
                        <div className="energy-bar h-1.5 rounded-full" style={{ width: `${m.journey.energy}%` }} />
                      </div>
                    </div>
                    <div className="space-y-2">
                      {m.journey.picks.map((p, pi) => (
                        <div key={pi} className="flex items-center gap-3 p-2 rounded-xl bg-white/[0.03] border border-white/5">
                          {p.artwork_url ? (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img src={p.artwork_url} alt="" className="w-10 h-10 rounded-lg object-cover shrink-0" />
                          ) : (
                            <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center shrink-0">
                              <Music2 size={16} className="text-white/40" />
                            </div>
                          )}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="text-[12px] font-bold truncate">{p.track}</span>
                              <span className="text-[10px] text-white/40 shrink-0">· {p.artist}</span>
                              {p.source && (
                                <span
                                  className={`text-[9px] font-bold uppercase shrink-0 ${
                                    p.source === "spotify" ? "text-emerald-400" : "text-white/30"
                                  }`}
                                >
                                  {p.source}
                                </span>
                              )}
                            </div>
                            <p className="text-[11px] text-white/50 leading-snug mt-0.5">{p.why}</p>
                          </div>
                          <div className="flex flex-col items-end gap-1 shrink-0">
                            {p.preview_url && (() => {
                              const pickId = `${p.artist}-${p.track}-${pi}`;
                              const isActive = nowPlaying?.id === pickId;
                              return (
                                <button
                                  onClick={() => playPick(m.journey!, pi)}
                                  aria-label={isActive && playing ? `Pause preview of ${p.track}` : `Play preview of ${p.track}`}
                                  className="w-7 h-7 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center hover:bg-emerald-500/30"
                                >
                                  {isActive && playing ? (
                                    <Pause size={12} className="fill-current" />
                                  ) : (
                                    <Play size={12} className="fill-current" />
                                  )}
                                </button>
                              );
                            })()}
                            <span className="text-[9px] text-white/30">{p.novelty_score}% new</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </GlassCard>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-blue-500 flex items-center justify-center shrink-0">
                <Bot size={16} className="text-black" />
              </div>
              <div className="glass-card px-4 py-3 flex gap-1.5 items-center">
                {[0, 150, 300].map((d) => (
                  <div
                    key={d}
                    className="w-1.5 h-1.5 rounded-full bg-emerald-400"
                    style={{ animation: `blob-float 1s ${d}ms ease-in-out infinite` }}
                  />
                ))}
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
          className="flex gap-3 mt-4"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tell Aura how you feel…"
            className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-[14px] placeholder:text-white/30 focus:outline-none focus:border-emerald-500/50 transition-colors"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            aria-label="Send message"
            className="px-5 py-3 rounded-xl bg-emerald-500 text-black font-black text-[14px] hover:brightness-110 disabled:opacity-40 transition-all"
          >
            <ArrowRight size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default function CompanionPage() {
  return (
    <Suspense fallback={null}>
      <CompanionView />
    </Suspense>
  );
}
