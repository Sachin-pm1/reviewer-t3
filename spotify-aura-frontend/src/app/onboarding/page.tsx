"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Briefcase, Home, GraduationCap, Rocket, Sunrise, Sun, Sunset, Moon,
  Flower2, Zap, Target, Drama, Dumbbell, Car, UtensilsCrossed,
  Sparkles, ArrowRight,
} from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import { useAuth } from "@/lib/auth-context";
import { isOnboardingComplete, setOnboardingComplete } from "@/lib/onboarding";

const STEPS = [
  {
    title: "What does a typical weekday look like?",
    options: [
      { icon: Briefcase, label: "Office job (9–6)" },
      { icon: Home, label: "Work from home" },
      { icon: GraduationCap, label: "Student" },
      { icon: Rocket, label: "Entrepreneur / Freelancer" },
    ],
  },
  {
    title: "When are you most productive?",
    options: [
      { icon: Sunrise, label: "Early bird (6–10 AM)" },
      { icon: Sun, label: "Mid morning (10–12)" },
      { icon: Sunset, label: "Afternoon (2–6 PM)" },
      { icon: Moon, label: "Night owl (10 PM+)" },
    ],
  },
  {
    title: "What do you want from music?",
    options: [
      { icon: Flower2, label: "Calm & stress relief" },
      { icon: Zap, label: "Energy & motivation" },
      { icon: Target, label: "Focus & productivity" },
      { icon: Drama, label: "Mood match & emotional support" },
    ],
  },
  {
    title: "What contexts matter most to you?",
    options: [
      { icon: Dumbbell, label: "Workouts" },
      { icon: Car, label: "Commute" },
      { icon: Moon, label: "Sleep" },
      { icon: UtensilsCrossed, label: "Meals & breaks" },
    ],
    multi: true,
  },
];

export default function AuraOnboarding() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [step, setStep] = useState(0);
  const [selections, setSelections] = useState<Record<number, number[]>>({});

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/signin");
      return;
    }
    if (!loading && user && isOnboardingComplete()) {
      router.replace("/dashboard");
    }
  }, [loading, user, router]);

  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;
  const selected = selections[step] ?? [];

  function toggle(i: number) {
    if (current.multi) {
      setSelections(s => {
        const prev = s[step] ?? [];
        return { ...s, [step]: prev.includes(i) ? prev.filter(x => x !== i) : [...prev, i] };
      });
    } else {
      setSelections(s => ({ ...s, [step]: [i] }));
    }
  }

  return (
    <div className="aura-bg min-h-screen flex items-center justify-center p-4 sm:p-6 text-white">
      <AuroraBlobs />
      <div className="relative w-full max-w-lg">
        {/* Progress */}
        <div className="flex gap-2 mb-10">
          {STEPS.map((_, i) => (
            <div key={i} className="flex-1 h-1 rounded-full overflow-hidden bg-white/10">
              <div className={`h-full rounded-full transition-all duration-500 ${i <= step ? "bg-emerald-400" : ""}`} style={{ width: i < step ? "100%" : i === step ? "50%" : "0%" }} />
            </div>
          ))}
        </div>

        <div className="text-center mb-8 slide-up">
          <p className="text-white/40 text-[12px] uppercase tracking-widest mb-3">Step {step + 1} of {STEPS.length}</p>
          <h2 className="text-2xl font-black leading-snug">{current.title}</h2>
          {current.multi && <p className="text-white/40 text-[13px] mt-2">Select all that apply</p>}
        </div>

        <div className="grid grid-cols-2 gap-3 mb-8 slide-up">
          {current.options.map((opt, i) => (
            <button
              key={i}
              onClick={() => toggle(i)}
              className={`glass-card p-5 flex flex-col items-center gap-3 transition-all duration-200 ${selected.includes(i) ? "border-emerald-500/60 bg-emerald-500/10 scale-[1.02]" : "hover:border-white/20"}`}
            >
              <opt.icon size={26} />
              <span className="text-[13px] font-bold text-center">{opt.label}</span>
            </button>
          ))}
        </div>

        <div className="flex gap-3">
          {step > 0 && (
            <button onClick={() => setStep(s => s - 1)} className="flex-1 py-3 rounded-xl glass-card text-white/60 font-bold text-[14px] hover:text-white transition-colors">
              Back
            </button>
          )}
          {isLast ? (
            <button
              onClick={() => {
                setOnboardingComplete(true);
                router.replace("/dashboard");
              }}
              className="flex-1 py-3 rounded-xl bg-emerald-500 text-black font-black text-[15px] text-center hover:brightness-110 transition-all flex items-center justify-center gap-1.5"
            >
              Enter Aura <Sparkles size={15} />
            </button>
          ) : (
            <button
              onClick={() => setStep(s => s + 1)}
              disabled={selected.length === 0}
              className="flex-1 py-3 rounded-xl bg-emerald-500 text-black font-black text-[15px] hover:brightness-110 disabled:opacity-30 transition-all flex items-center justify-center gap-1.5"
            >
              Continue <ArrowRight size={15} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
