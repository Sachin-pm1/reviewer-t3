"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Music, Search, ListMusic, Bot, X, Sunrise, Car, Laptop,
  UtensilsCrossed, Dumbbell, Sunset, Moon, Headphones, Dna, BookOpen,
  Sparkles, Play, ArrowRight, Monitor, Smartphone, Watch, LogIn, UserPlus,
} from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GradientText } from "@/components/GradientText";
import { GlassCard } from "@/components/GlassCard";
import { AuraBadge } from "@/components/AuraBadge";
import { useAuth } from "@/lib/auth-context";
import { isOnboardingComplete } from "@/lib/onboarding";

const STATS = [
  { icon: Music,     stat: "120M+", label: "Songs", problem: "Choice Overload" },
  { icon: Search,    stat: "∞",     label: "Endless Searching", problem: "Decision Fatigue" },
  { icon: ListMusic, stat: null,    label: "Static Playlists", problem: "Same Music Every Day" },
  { icon: Bot,       stat: null,    statIcon: X, label: "Generic Recs", problem: "Missing Emotional Context" },
];

const TIMELINE = [
  { time: "7am",  icon: Sunrise, label: "Wake Up",  color: "#F97316" },
  { time: "8am",  icon: Car,     label: "Commute",  color: "#3B82F6" },
  { time: "10am", icon: Laptop,  label: "Work",     color: "#8B5CF6" },
  { time: "1pm",  icon: UtensilsCrossed, label: "Lunch", color: "#14B8A6" },
  { time: "6pm",  icon: Dumbbell, label: "Workout", color: "#EC4899" },
  { time: "8pm",  icon: Sunset,  label: "Evening",  color: "#F59E0B" },
  { time: "11pm", icon: Moon,    label: "Sleep",    color: "#6366F1" },
];

const PILLARS = [
  {
    icon: Headphones,
    title: "Adaptive Listening",
    desc: "Music that evolves with your day, mood, energy, and context — automatically, without a single tap.",
    color: "from-emerald-500/20 to-blue-500/20",
    border: "border-emerald-500/20",
  },
  {
    icon: Dna,
    title: "Music DNA",
    desc: "Your listening habits reveal your personality. Discover your Explorer, Dreamer, Builder, or Night Owl self.",
    color: "from-purple-500/20 to-pink-500/20",
    border: "border-purple-500/20",
  },
  {
    icon: BookOpen,
    title: "Life Chapters",
    desc: "Every major life moment — your MBA, first job, a road trip — preserved as a cinematic music story.",
    color: "from-blue-500/20 to-teal-500/20",
    border: "border-blue-500/20",
  },
];

export default function AuraLanding() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [hoveredStep, setHoveredStep] = useState<number | null>(null);
  const [hoveredPillar, setHoveredPillar] = useState<number | null>(null);

  useEffect(() => {
    if (!loading && user) {
      router.replace(isOnboardingComplete() ? "/dashboard" : "/onboarding");
    }
  }, [loading, user, router]);

  return (
    <div className="aura-bg text-white">
      <AuroraBlobs />

      {/* ── Top bar — always visible on the public landing page ── */}
      <header className="relative flex items-center justify-between px-4 sm:px-8 py-5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-blue-500 flex items-center justify-center">
            <Music size={16} className="text-black" />
          </div>
          <span className="text-[14px] font-black tracking-tight gradient-text">Spotify Aura</span>
        </div>
        {!loading && !user && (
          <div className="flex items-center gap-2">
            <Link
              href="/signin"
              className="px-4 py-2 rounded-full border border-white/15 text-white/80 text-[13px] font-bold hover:text-white hover:border-white/30 transition-colors inline-flex items-center gap-1.5"
            >
              <LogIn size={13} /> Sign in
            </Link>
            <Link
              href="/signup"
              className="px-4 py-2 rounded-full bg-[#1DB954] text-black text-[13px] font-black hover:brightness-110 transition-all inline-flex items-center gap-1.5"
            >
              <UserPlus size={13} /> Sign up
            </Link>
          </div>
        )}
      </header>

      {/* ── Hero ── */}
      <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-4 sm:px-8 py-14 sm:py-20">
        <div className="slide-up" style={{ animationDelay: "0ms" }}>
          <AuraBadge color="green" className="mb-6 text-[12px] px-4 py-1">
            <Sparkles size={12} /> Spotify Vision 2030
          </AuraBadge>
          <h1 className="text-6xl md:text-7xl font-black leading-tight mb-6 max-w-4xl">
            <GradientText>The World&apos;s First</GradientText>
            <br />
            <span className="text-white">AI Life Soundtrack</span>
            <br />
            <GradientText>Platform.</GradientText>
          </h1>
          <p className="text-xl text-white/60 max-w-2xl mx-auto mb-4 leading-relaxed font-light">
            Music shouldn&apos;t just match your taste.
            <br />
            <span className="text-white/90 font-medium">It should understand your life.</span>
          </p>
          <p className="text-[15px] text-white/45 max-w-xl mx-auto mb-10">
            Spotify Aura transforms music from passive listening into an adaptive AI-powered Life Soundtrack
            that evolves throughout your day.
          </p>
          <div className="flex items-center gap-4 justify-center flex-wrap">
            <Link
              href="/onboarding"
              className="px-8 py-3.5 rounded-full bg-[#1DB954] text-black font-black text-[15px] hover:brightness-110 transition-all hover:scale-105 inline-flex items-center gap-1.5"
            >
              Explore Aura <Sparkles size={15} />
            </Link>
            <Link
              href="/future"
              className="px-8 py-3.5 rounded-full glass-card text-white font-bold text-[15px] hover:border-white/30 inline-flex items-center gap-1.5"
            >
              <Play size={13} className="fill-current" /> Watch Product Demo
            </Link>
          </div>
        </div>

        {/* Floating music cards */}
        <div className="absolute top-24 right-12 glass-card px-4 py-3 rotate-3 hidden xl:block" style={{ animationDelay: "0.5s" }}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-blue-500 flex items-center justify-center"><Music size={18} /></div>
            <div className="text-left">
              <div className="text-[13px] font-bold">Blinding Lights</div>
              <div className="text-[11px] text-white/50">Morning Commute · High Energy</div>
            </div>
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse ml-2" />
          </div>
        </div>
        <div className="absolute bottom-32 left-10 glass-card px-4 py-3 -rotate-2 hidden xl:block">
          <div className="text-[12px] text-white/60 mb-1 flex items-center gap-1"><Bot size={13} /> Aura says</div>
          <div className="text-[13px] font-medium">"Rainy afternoon detected.<br/>Switching to Lo-fi..."</div>
        </div>
      </section>

      {/* ── Problem Stats ── */}
      <section className="relative px-4 sm:px-8 py-14 sm:py-20">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-white/40 text-[13px] uppercase tracking-widest mb-3 font-bold">The Problem</p>
            <h2 className="text-4xl font-black">
              Today&apos;s Spotify is <GradientText>stuck in the past.</GradientText>
            </h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {STATS.map((s, i) => {
              const StatIcon = s.statIcon;
              return (
                <GlassCard key={i} className="text-center py-8">
                  <div className="flex justify-center mb-3"><s.icon size={32} /></div>
                  <div className="text-2xl font-black text-white mb-1 h-8 flex items-center justify-center">
                    {s.stat ?? (StatIcon ? <StatIcon size={22} /> : <ListMusic size={22} />)}
                  </div>
                  <div className="text-[13px] text-white/70 font-semibold mb-2">{s.label}</div>
                  <div className="text-[11px] text-red-400 font-bold flex items-center justify-center gap-1">
                    <ArrowRight size={11} /> {s.problem}
                  </div>
                </GlassCard>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── Vision Timeline ── */}
      <section className="relative px-4 sm:px-8 py-14 sm:py-20">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-white/40 text-[13px] uppercase tracking-widest mb-3 font-bold">The Vision</p>
            <h2 className="text-4xl font-black mb-4">
              One adaptive soundtrack for <GradientText>every moment.</GradientText>
            </h2>
            <p className="text-white/50 max-w-xl mx-auto">
              Aura plans your entire day&apos;s music like Google Maps plans your route — automatically adjusting as your day unfolds.
            </p>
          </div>

          <div className="flex items-center justify-center gap-0 flex-wrap">
            {TIMELINE.map((step, i) => (
              <div key={i} className="flex items-center">
                <button
                  onMouseEnter={() => setHoveredStep(i)}
                  onMouseLeave={() => setHoveredStep(null)}
                  className="relative flex flex-col items-center gap-2 px-4 py-4 rounded-2xl transition-all duration-300 group"
                  style={{
                    background: hoveredStep === i ? `${step.color}22` : "transparent",
                    transform: hoveredStep === i ? "scale(1.1)" : "scale(1)",
                  }}
                >
                  <div
                    className="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl transition-all duration-300"
                    style={{
                      background: `${step.color}20`,
                      border: `1px solid ${step.color}40`,
                      boxShadow: hoveredStep === i ? `0 0 24px ${step.color}50` : "none",
                    }}
                  >
                    <step.icon size={22} style={{ color: step.color }} />
                  </div>
                  <div className="text-[12px] font-bold text-white/80">{step.label}</div>
                  <div className="text-[10px] text-white/40">{step.time}</div>
                </button>
                {i < TIMELINE.length - 1 && (
                  <div className="w-6 h-px bg-white/10 mx-1" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Product Pillars ── */}
      <section className="relative px-4 sm:px-8 py-14 sm:py-20">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-white/40 text-[13px] uppercase tracking-widest mb-3 font-bold">Product Pillars</p>
            <h2 className="text-4xl font-black">
              Built on three <GradientText>core experiences.</GradientText>
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {PILLARS.map((p, i) => (
              <div
                key={i}
                onMouseEnter={() => setHoveredPillar(i)}
                onMouseLeave={() => setHoveredPillar(null)}
                className={`glass-card grad-border p-8 flex flex-col gap-4 cursor-pointer bg-gradient-to-br ${p.color} border ${p.border}`}
                style={{ transform: hoveredPillar === i ? "translateY(-8px)" : undefined }}
              >
                <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center"><p.icon size={24} /></div>
                <h3 className="text-xl font-black">{p.title}</h3>
                <p className="text-white/60 text-[14px] leading-relaxed">{p.desc}</p>
                <button className="mt-auto text-[13px] font-bold text-emerald-400 hover:text-emerald-300 flex items-center gap-1.5">
                  Learn More <ArrowRight size={13} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Device Showcase ── */}
      <section className="relative px-4 sm:px-8 py-14 sm:py-20">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-white/40 text-[13px] uppercase tracking-widest mb-3 font-bold">Available Everywhere</p>
          <h2 className="text-4xl font-black mb-12">
            One soundtrack across <GradientText>all your devices.</GradientText>
          </h2>
          <div className="flex items-end justify-center gap-6 flex-wrap">
            {/* Desktop */}
            <div className="glass-card p-6 w-72 slide-up" style={{ animationDelay: "100ms" }}>
              <div className="bg-black/40 rounded-xl p-4 mb-4 aspect-video flex items-center justify-center">
                <div className="text-center">
                  <div className="flex justify-center mb-2"><Monitor size={26} /></div>
                  <div className="text-[12px] text-white/50">Desktop</div>
                </div>
              </div>
              <div className="text-[13px] font-bold text-white/80">Full Dashboard</div>
              <div className="text-[11px] text-white/40 mt-1">Complete control & insights</div>
            </div>
            {/* Phone */}
            <div className="glass-card p-4 w-44 slide-up" style={{ animationDelay: "200ms" }}>
              <div className="bg-black/40 rounded-xl p-4 mb-3 aspect-[9/16] flex items-center justify-center">
                <div className="text-center">
                  <div className="flex justify-center mb-2"><Smartphone size={26} /></div>
                  <div className="text-[11px] text-white/50">Mobile</div>
                  <div className="mt-3 flex flex-col gap-1.5">
                    <div className="h-1 bg-gradient-to-r from-emerald-400 to-blue-500 rounded-full w-full" />
                    <div className="h-1 bg-white/10 rounded-full w-3/4 mx-auto" />
                  </div>
                </div>
              </div>
              <div className="text-[12px] font-bold text-white/80">On the Go</div>
              <div className="text-[10px] text-white/40 mt-0.5">Adaptive & always with you</div>
            </div>
            {/* Watch */}
            <div className="glass-card p-4 w-36 slide-up" style={{ animationDelay: "300ms" }}>
              <div className="bg-black/40 rounded-xl p-4 mb-3 aspect-square flex items-center justify-center">
                <div className="text-center">
                  <div className="flex justify-center mb-1"><Watch size={20} /></div>
                  <div className="text-[10px] text-white/50">Watch</div>
                </div>
              </div>
              <div className="text-[11px] font-bold text-white/80">Wrist</div>
              <div className="text-[10px] text-white/40 mt-0.5">Heart rate aware</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="relative px-4 sm:px-8 py-10 sm:py-14 border-t border-white/5 text-center">
        <div className="text-[13px] text-white/30 font-medium tracking-widest uppercase">
          Spotify Vision 2030 — Designed for the Future of Music
        </div>
        <Link
          href="/onboarding"
          className="inline-flex items-center gap-1.5 mt-6 px-10 py-4 rounded-full bg-gradient-to-r from-emerald-500 to-blue-500 text-white font-black text-[15px] hover:brightness-110 transition-all hover:scale-105"
        >
          Enter the Experience <Sparkles size={15} />
        </Link>
      </footer>
    </div>
  );
}
