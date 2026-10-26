"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Home, Sparkles, Music, Bot, Dna, BookOpen, Telescope, Camera,
  BarChart3, Settings, Target, Car, Dumbbell, Star, Rocket, Menu, X,
  LogIn, LogOut, UserPlus,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";
import { isOnboardingComplete } from "@/lib/onboarding";
import { AudioPlayerProvider, useAudioPlayer } from "@/lib/audio-player-context";
import { MiniPlayer } from "@/components/MiniPlayer";

const NAV = [
  { href: "/",             icon: Home,       label: "Home" },
  { href: "/dashboard",    icon: Sparkles,   label: "Dashboard" },
  { href: "/soundtrack",   icon: Music,      label: "Life Soundtrack" },
  { href: "/companion",    icon: Bot,        label: "AI Companion" },
  { href: "/dna",          icon: Dna,        label: "Music DNA" },
  { href: "/chapters",     icon: BookOpen,   label: "Life Chapters" },
  { href: "/discovery",    icon: Telescope,  label: "Discovery" },
  { href: "/memories",     icon: Camera,     label: "Memories" },
  { href: "/insights",     icon: BarChart3,  label: "Insights" },
  { href: "/settings",     icon: Settings,   label: "Settings" },
  { href: "/onboarding",   icon: Target,     label: "Onboarding" },
  { href: "/commute",      icon: Car,        label: "Commute Mode" },
  { href: "/workout",      icon: Dumbbell,   label: "Workout Coach" },
  { href: "/wrapped",      icon: Star,       label: "Year in Life" },
  { href: "/future",       icon: Rocket,     label: "Future Vision" },
];

export default function LayoutShell({ children }: { children: React.ReactNode }) {
  return (
    <AudioPlayerProvider>
      <LayoutShellInner>{children}</LayoutShellInner>
    </AudioPlayerProvider>
  );
}

function LayoutShellInner({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [onboardingComplete, setOnboardingComplete] = useState(false);
  const { user, loading, signOut } = useAuth();
  const { current: nowPlaying } = useAudioPlayer();

  const isAuthPage = pathname === "/signin" || pathname === "/signup";
  const isPublicPage = pathname === "/" || isAuthPage;
  // Show on every non-public page regardless of auth state — the account
  // section below already renders Sign in/up links when logged out, so
  // gating the whole sidebar on `user` just strands a logged-out visitor
  // (or someone whose session just expired) with no navigation at all.
  const showSidebar = !loading && !isPublicPage;

  useEffect(() => {
    setOpen(false);
    setOnboardingComplete(isOnboardingComplete());
  }, [pathname]);

  useEffect(() => {
    const handleChanged = () => setOnboardingComplete(isOnboardingComplete());
    window.addEventListener("aura:onboarding-changed", handleChanged);
    return () => window.removeEventListener("aura:onboarding-changed", handleChanged);
  }, []);

  function handleSignOut() {
    signOut();
    router.push("/signin");
  }

  const navItems = NAV.filter((item) => item.href !== "/onboarding" || !onboardingComplete);

  return (
    <div className="flex h-screen bg-[#050508] text-white overflow-hidden">
      {/* Mobile top bar */}
      <div className="lg:hidden fixed top-0 inset-x-0 z-40 flex items-center justify-between px-4 py-3 border-b border-white/5 bg-black/50 backdrop-blur-xl">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-emerald-400 to-blue-500 flex items-center justify-center">
            <Music size={14} className="text-black" />
          </div>
          <div className="text-[13px] font-black tracking-tight gradient-text">Spotify Aura</div>
        </div>
        <button
          onClick={() => setOpen((v) => !v)}
          aria-label={open ? "Close navigation menu" : "Open navigation menu"}
          aria-expanded={open}
          className="w-9 h-9 rounded-lg border border-white/10 flex items-center justify-center text-white/70 hover:text-white hover:border-white/20 transition-colors"
        >
          {open ? <X size={16} /> : <Menu size={16} />}
        </button>
      </div>

      {/* Backdrop (mobile only, when drawer is open) */}
      {open && (
        <div
          onClick={() => setOpen(false)}
          className="lg:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
        />
      )}

      {/* Sidebar — static column on desktop, slide-in drawer on mobile */}
      {showSidebar && (
      <aside
        className={cn(
          "w-[220px] shrink-0 flex flex-col border-r border-white/5 bg-black/70 lg:bg-black/30 backdrop-blur-xl overflow-y-auto",
          "fixed inset-y-0 left-0 z-50 transition-transform duration-300 lg:static lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="px-4 py-5 border-b border-white/5">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-blue-500 flex items-center justify-center">
              <Music size={16} className="text-black" />
            </div>
            <div>
              <div className="text-[13px] font-black tracking-tight gradient-text">Spotify Aura</div>
              <div className="text-[10px] text-white/40 font-medium">Discovery MVP</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 py-3 px-2 space-y-0.5">
          {navItems.map((item) => {
            const active = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-2.5 px-3 py-2 rounded-xl text-[12px] font-semibold transition-all",
                  active
                    ? "bg-white/10 text-white border border-white/10"
                    : "text-white/50 hover:text-white hover:bg-white/5"
                )}
              >
                <Icon size={14} />
                <span>{item.label}</span>
                {active && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-400" />
                )}
              </Link>
            );
          })}
        </nav>

        <div className="px-3 py-3 border-t border-white/5">
          {loading ? null : user ? (
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center text-[11px] font-bold shrink-0">
                {user.email[0]?.toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[11px] font-semibold truncate">{user.email}</div>
              </div>
              <button
                onClick={handleSignOut}
                aria-label="Sign out"
                className="w-7 h-7 rounded-lg flex items-center justify-center text-white/40 hover:text-white hover:bg-white/5 transition-colors shrink-0"
              >
                <LogOut size={14} />
              </button>
            </div>
          ) : (
            <div className="flex gap-2">
              <Link
                href="/signin"
                className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg border border-white/10 text-[11px] font-semibold text-white/70 hover:text-white hover:border-white/20 transition-colors"
              >
                <LogIn size={12} /> Sign in
              </Link>
              <Link
                href="/signup"
                className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-emerald-500 text-black text-[11px] font-bold hover:brightness-110 transition-all"
              >
                <UserPlus size={12} /> Sign up
              </Link>
            </div>
          )}
        </div>
      </aside>
      )}

      {/* Main content */}
      <main
        className={cn(
          "flex-1 overflow-y-auto overflow-x-hidden pt-14 lg:pt-0 w-full min-w-0",
          nowPlaying && "pb-16"
        )}
      >
        {children}
      </main>

      <MiniPlayer />
    </div>
  );
}
