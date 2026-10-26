"use client";

import Link from "next/link";
import { Headphones, Brain, AudioLines, Globe, Dna, Sparkles } from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import { AuraBadge } from "@/components/AuraBadge";

const VISIONS = [
  {
    year: "2025", icon: Headphones, title: "Emotional Intelligence",
    desc: "Aura learns your emotional patterns from 50+ daily signals — weather, calendar, heart rate, location, sleep. Music becomes truly contextual.",
    status: "live", color: "#1DB954",
  },
  {
    year: "2026", icon: Brain, title: "Predictive Soundscaping",
    desc: "Aura predicts your mood state 30 minutes ahead using pattern recognition and pre-buffers the perfect soundtrack before you even feel it.",
    status: "building", color: "#3B82F6",
  },
  {
    year: "2027", icon: AudioLines, title: "Generative Composition",
    desc: "Aura composes original music in real-time — personalised to your DNA, mood, and moment. No two people hear the same track.",
    status: "research", color: "#8B5CF6",
  },
  {
    year: "2028", icon: Globe, title: "Social Aura Sync",
    desc: "When two Aura users meet, your soundscapes blend into a shared musical experience — perfect harmony for every human connection.",
    status: "vision", color: "#EC4899",
  },
  {
    year: "2029", icon: Dna, title: "Biometric Music Therapy",
    desc: "Clinical-grade music therapy delivered through sound — reducing anxiety, improving sleep, and supporting mental health at scale.",
    status: "vision", color: "#14B8A6",
  },
  {
    year: "2030", icon: Sparkles, title: "Life as a Symphony",
    desc: "Your entire life becomes a living composition — every memory, every chapter, every emotion woven into a musical legacy that is uniquely yours.",
    status: "dream", color: "#F97316",
  },
];

const STATUS_CONFIG: Record<string, { label: string; color: "green" | "blue" | "purple" | "pink" | "teal" | "orange" }> = {
  live:     { label: "Live Now",    color: "green"  },
  building: { label: "In Progress", color: "blue"   },
  research: { label: "Research",    color: "purple" },
  vision:   { label: "Vision",      color: "pink"   },
  dream:    { label: "Dream",       color: "orange" },
};

export default function AuraFuture() {
  return (
    <div className="aura-bg min-h-screen p-4 sm:p-6 lg:p-8 text-white">
      <AuroraBlobs />

      {/* Cinematic hero */}
      <div className="relative max-w-5xl mx-auto text-center py-10 sm:py-16 mb-12">
        <AuraBadge color="purple" className="mb-6 text-[13px] px-4 py-1.5">Vision 2030</AuraBadge>
        <h1 className="text-4xl sm:text-6xl font-black leading-tight mb-6">
          The Future of<br /><GradientText>Human Experience</GradientText><br />Is Sonic.
        </h1>
        <p className="text-white/50 text-[17px] max-w-2xl mx-auto leading-relaxed mb-10">
          Music is not just entertainment. It is the emotional infrastructure of the human experience.
          Aura&apos;s mission is to put the perfect soundtrack to every moment of every life on earth.
        </p>

        {/* Giant stat */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-2xl mx-auto">
          {[["5B+", "People we want to reach"], ["50+", "Life signals synthesised"], ["∞", "Unique soundscapes"]].map(([v, l]) => (
            <GlassCard key={l} className="py-8">
              <div className="text-4xl font-black gradient-text mb-2">{v}</div>
              <div className="text-[12px] text-white/50">{l}</div>
            </GlassCard>
          ))}
        </div>
      </div>

      {/* Roadmap timeline */}
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl font-black mb-8 text-center text-white/80">The Roadmap to 2030</h2>
        <div className="relative">
          {/* Centre line — desktop only; mobile uses a left-aligned line instead */}
          <div className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-emerald-500 via-purple-500 to-orange-500 -translate-x-1/2" />
          <div className="lg:hidden absolute left-[9px] top-0 bottom-0 w-0.5 bg-gradient-to-b from-emerald-500 via-purple-500 to-orange-500" />

          <div className="space-y-8">
            {VISIONS.map((v, i) => (
              <div key={i} className={`relative lg:static flex items-start lg:items-center gap-4 sm:gap-8 pl-8 lg:pl-0 ${i % 2 === 0 ? "" : "lg:flex-row-reverse"}`}>
                <div className={`flex-1 min-w-0 text-left ${i % 2 === 0 ? "lg:text-right" : "lg:text-left"}`}>
                  <GlassCard style={{ borderColor: `${v.color}30`, background: `${v.color}06` }}>
                    <div className={`flex items-center gap-2 mb-2 justify-start ${i % 2 === 0 ? "lg:justify-end" : "lg:justify-start"}`}>
                      <AuraBadge color={STATUS_CONFIG[v.status].color}>{STATUS_CONFIG[v.status].label}</AuraBadge>
                      <span className="text-[12px] text-white/40 font-bold">{v.year}</span>
                    </div>
                    <div className="flex items-center gap-2 mb-2" style={{ justifyContent: "flex-start" }}>
                      <v.icon size={20} style={{ color: v.color }} />
                      <h3 className="text-[17px] font-black">{v.title}</h3>
                    </div>
                    <p className="text-[13px] text-white/60 leading-relaxed">{v.desc}</p>
                  </GlassCard>
                </div>

                {/* Node on timeline */}
                <div
                  className="absolute left-0 top-1 lg:static w-5 h-5 rounded-full border-4 border-black shrink-0 z-10 shadow-lg"
                  style={{ background: v.color }}
                />

                <div className="hidden lg:block flex-1" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="max-w-2xl mx-auto text-center mt-20 py-12">
        <div className="flex justify-center mb-6"><Sparkles size={44} className="text-yellow-400" /></div>
        <h2 className="text-3xl font-black mb-4">This is just the beginning.</h2>
        <p className="text-white/50 text-[15px] mb-8 leading-relaxed">
          Every great product starts as a vision. Aura was born from one simple belief:
          your life deserves a perfect soundtrack, every single day.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/dashboard" className="px-8 py-4 rounded-2xl bg-emerald-500 text-black font-black text-[15px] hover:brightness-110 transition-all text-center">
            Experience Aura Today
          </Link>
          <Link href="/onboarding" className="px-8 py-4 rounded-2xl glass-card font-black text-[15px] hover:border-white/20 transition-all text-center">
            Start Your Journey
          </Link>
        </div>
      </div>
    </div>
  );
}
