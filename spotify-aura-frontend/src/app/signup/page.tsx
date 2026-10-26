"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { UserPlus } from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import { useAuth, authErrorMessage } from "@/lib/auth-context";
import { isOnboardingComplete } from "@/lib/onboarding";

export default function SignUpPage() {
  const router = useRouter();
  const { user, loading: authLoading, signUp } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!authLoading && user) {
      router.replace(isOnboardingComplete() ? "/dashboard" : "/onboarding");
    }
  }, [authLoading, user, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError("Password needs to be at least 8 characters.");
      return;
    }
    setLoading(true);
    try {
      await signUp(email, password);
      router.replace(isOnboardingComplete() ? "/dashboard" : "/onboarding");
    } catch (err) {
      setError(authErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="aura-bg min-h-screen flex items-center justify-center p-4 sm:p-6 text-white">
      <AuroraBlobs />
      <div className="relative w-full max-w-sm">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-black mb-2">
            <GradientText>Create your account.</GradientText>
          </h1>
          <p className="text-white/50 text-[13px]">Your taste profile follows you across devices.</p>
        </div>
        <GlassCard className="space-y-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-[11px] text-white/50 font-bold uppercase tracking-wide">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="mt-1.5 w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-[13px] placeholder:text-white/25 focus:outline-none focus:border-emerald-500/50"
              />
            </div>
            <div>
              <label className="text-[11px] text-white/50 font-bold uppercase tracking-wide">Password</label>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 8 characters"
                className="mt-1.5 w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-[13px] placeholder:text-white/25 focus:outline-none focus:border-emerald-500/50"
              />
            </div>
            {error && <p className="text-[12px] text-red-400">{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-emerald-500 text-black font-black text-[14px] hover:brightness-110 disabled:opacity-50 transition-all flex items-center justify-center gap-1.5"
            >
              <UserPlus size={14} /> {loading ? "Creating account…" : "Create account"}
            </button>
          </form>
        </GlassCard>
        <p className="text-center text-[12px] text-white/40 mt-4">
          Already have an account?{" "}
          <Link href="/signin" className="text-emerald-400 font-semibold hover:text-emerald-300">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
