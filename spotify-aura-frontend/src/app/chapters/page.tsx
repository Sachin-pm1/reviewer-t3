"use client";

import Link from "next/link";
import { BookOpen, ArrowRight } from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";

export default function AuraChapters() {
  return (
    <div className="aura-bg min-h-screen p-4 sm:p-6 lg:p-8 text-white">
      <AuroraBlobs />
      <div className="relative w-full max-w-2xl mx-auto">
        <div className="mb-8">
          <p className="text-white/40 text-[12px] uppercase tracking-widest mb-2 font-bold">Your Story in Music</p>
          <h1 className="text-3xl sm:text-4xl font-black mb-2"><GradientText>Life Chapters</GradientText></h1>
        </div>

        <GlassCard className="text-center py-16">
          <BookOpen size={36} className="text-white/20 mx-auto mb-4" />
          <p className="text-white/60 text-[14px] mb-2 max-w-md mx-auto">
            This feature can&apos;t honestly be built with real data.
          </p>
          <p className="text-white/40 text-[13px] mb-6 max-w-md mx-auto leading-relaxed">
            Spotify&apos;s API doesn&apos;t expose multi-year historical listening logs at any
            permission level — there&apos;s no endpoint that returns what you were playing back in
            2022, or when your taste shifted. Building a real &quot;life story&quot; view would need
            years of your own logged listening data from an external source, which this app
            doesn&apos;t have.
          </p>
          <Link href="/memories" className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full bg-emerald-500 text-black text-[13px] font-black hover:brightness-110 transition-all">
            Try Memories instead <ArrowRight size={14} />
          </Link>
          <p className="text-white/30 text-[11px] mt-2">Real recent plays, plus your own notes for any day.</p>
        </GlassCard>
      </div>
    </div>
  );
}
