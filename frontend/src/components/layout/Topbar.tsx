"use client";

import { Compass, Menu, Zap, ZapOff } from "lucide-react";
import { useHealth } from "@/lib/hooks";

interface TopbarProps {
  onMenuClick: () => void;
}

export function Topbar({ onMenuClick }: TopbarProps) {
  const { data: health } = useHealth();

  return (
    <header className="flex items-center justify-between gap-3 px-3 sm:px-5 py-3 border-b border-[#2a2f3a] bg-[#171a21] h-[52px] shrink-0">
      <div className="flex items-center gap-2 min-w-0">
        <button
          onClick={onMenuClick}
          aria-label="Toggle project sidebar"
          className="lg:hidden shrink-0 w-7 h-7 flex items-center justify-center rounded-md text-[#9aa3b2] hover:bg-[#1e222b] hover:text-[#e7e9ee] transition-colors"
        >
          <Menu size={16} />
        </button>
        <Compass size={18} className="text-[#5b8cff] shrink-0" />
        <span className="font-bold text-[15px] tracking-tight truncate">
          <span className="hidden sm:inline">AI Product Intelligence</span>
          <span className="sm:hidden">AI Intelligence</span>
        </span>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        {health ? (
          health.ai_enabled ? (
            <div className="flex items-center gap-1.5 text-[12px] text-[#34d399] font-medium">
              <Zap size={13} />
              <span className="hidden md:inline">Claude {health.model} · AI enabled</span>
              <span className="md:hidden">AI on</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-[12px] text-[#fbbf24] font-medium">
              <ZapOff size={13} />
              <span className="hidden md:inline">No API key · AI disabled</span>
              <span className="md:hidden">AI off</span>
            </div>
          )
        ) : (
          <span className="text-[12px] text-[#9aa3b2]">checking…</span>
        )}
      </div>
    </header>
  );
}
