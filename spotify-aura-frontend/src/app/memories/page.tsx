"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Music, StickyNote, Play, Calendar, Pencil, Trash2, Plus, X, Sparkles } from "lucide-react";
import { AuroraBlobs } from "@/components/AuroraBlobs";
import { GlassCard } from "@/components/GlassCard";
import { GradientText } from "@/components/GradientText";
import { AuraBadge } from "@/components/AuraBadge";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Memory, SpotifyOverview, SpotifyRealTrack } from "@/lib/types";

const MOODS = ["Happy", "Motivated", "Reflective", "Free", "Nostalgic", "Energized", "Calm", "Peaceful"];

function pad2(n: number): string {
  return String(n).padStart(2, "0");
}

export default function AuraMemories() {
  const { user } = useAuth();
  const [overview, setOverview] = useState<SpotifyOverview | null>(null);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [noteDraft, setNoteDraft] = useState("");
  const [moodDraft, setMoodDraft] = useState<string>("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!user) return;
    api.spotifyConnect.overview().then(setOverview).catch(() => {});
    api.memories.list().then(setMemories).catch(() => {});
  }, [user]);

  const connected = overview?.connected ?? false;

  const now = useMemo(() => new Date(), []);
  const year = now.getFullYear();
  const month = now.getMonth(); // 0-indexed
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const leadingBlanks = (new Date(year, month, 1).getDay() + 6) % 7; // Monday-first offset
  const monthLabel = now.toLocaleDateString(undefined, { month: "long", year: "numeric" });

  function isoFor(day: number): string {
    return `${year}-${pad2(month + 1)}-${pad2(day)}`;
  }

  const realTracksByDate = useMemo(() => {
    const grouped: Record<string, SpotifyRealTrack[]> = {};
    for (const track of overview?.recently_played ?? []) {
      if (!track.played_at) continue;
      const d = new Date(track.played_at);
      const key = `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`;
      grouped[key] ??= [];
      grouped[key].push(track);
    }
    return grouped;
  }, [overview]);

  const memoriesByDate = useMemo(() => {
    const map: Record<string, Memory> = {};
    for (const m of memories) map[m.date] = m;
    return map;
  }, [memories]);

  const selectedRealTracks = selectedDate ? realTracksByDate[selectedDate] : undefined;
  const selectedManual = selectedDate ? memoriesByDate[selectedDate] : undefined;

  function openDay(day: number) {
    const iso = isoFor(day);
    setEditing(false);
    setSelectedDate(iso === selectedDate ? null : iso);
  }

  function startEditing() {
    setNoteDraft(selectedManual?.note ?? "");
    setMoodDraft(selectedManual?.mood ?? "");
    setEditing(true);
  }

  async function saveMemory() {
    if (!selectedDate || !noteDraft.trim()) return;
    setSaving(true);
    try {
      const saved = await api.memories.upsert({
        date: selectedDate,
        note: noteDraft.trim(),
        mood: moodDraft || null,
      });
      setMemories((prev) => [...prev.filter((m) => m.date !== saved.date), saved]);
      setEditing(false);
    } finally {
      setSaving(false);
    }
  }

  async function deleteMemory() {
    if (!selectedManual) return;
    setSaving(true);
    try {
      await api.memories.remove(selectedManual.id);
      setMemories((prev) => prev.filter((m) => m.id !== selectedManual.id));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="aura-bg min-h-screen p-4 sm:p-6 lg:p-8 text-white">
      <AuroraBlobs />
      <div className="relative w-full">
        <div className="mb-8">
          <p className="text-white/40 text-[12px] uppercase tracking-widest mb-2 font-bold">Your Musical Diary</p>
          <h1 className="text-3xl sm:text-4xl font-black mb-2"><GradientText>Memories</GradientText></h1>
          <p className="text-white/50 text-[14px]">Relive any day through the music you loved — and your own words.</p>
        </div>

        {!user ? (
          <GlassCard className="text-center py-16">
            <Sparkles size={36} className="text-white/20 mx-auto mb-4" />
            <p className="text-white/50 text-[14px] mb-4">Sign in to start adding real memories to any day.</p>
            <Link href="/signin" className="inline-flex px-5 py-2.5 rounded-full bg-emerald-500 text-black text-[13px] font-black hover:brightness-110 transition-all">Sign in</Link>
          </GlassCard>
        ) : (
          <>
            {!connected && (
              <div className="glass-card border-white/10 bg-white/[0.03] px-4 py-3 mb-6 text-[13px] text-white/40">
                Connect Spotify in <Link href="/settings" className="text-emerald-400 font-semibold hover:text-emerald-300">Settings</Link> to also see real tracks you played on each day.
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Calendar */}
              <div className="lg:col-span-1">
                <GlassCard>
                  <div className="text-[14px] font-black mb-4">{monthLabel}</div>
                  <div className="grid grid-cols-7 gap-1 text-center mb-2">
                    {["M","T","W","T","F","S","S"].map((d, i) => (
                      <div key={i} className="text-[10px] text-white/30 font-bold">{d}</div>
                    ))}
                  </div>
                  <div className="grid grid-cols-7 gap-1">
                    {Array.from({ length: leadingBlanks }, (_, i) => <div key={`blank-${i}`} />)}
                    {Array.from({ length: daysInMonth }, (_, i) => i + 1).map((day) => {
                      const iso = isoFor(day);
                      const hasContent = !!memoriesByDate[iso] || (realTracksByDate[iso]?.length ?? 0) > 0;
                      const isSelected = selectedDate === iso;
                      return (
                        <button
                          key={day}
                          onClick={() => openDay(day)}
                          aria-label={`${monthLabel.split(" ")[0]} ${day}${hasContent ? " — has a memory" : ""}`}
                          aria-pressed={isSelected}
                          className={`aspect-square rounded-lg text-[12px] font-bold flex items-center justify-center transition-all cursor-pointer
                            ${isSelected ? "bg-emerald-500 text-black" : hasContent ? "bg-white/10 text-white border border-emerald-500/30 hover:border-emerald-500/60" : "text-white/40 border border-white/5 hover:border-white/20"}
                          `}
                        >
                          {day}
                        </button>
                      );
                    })}
                  </div>
                  <div className="mt-4 text-[11px] text-white/30 flex items-center gap-2">
                    <div className="w-3 h-3 rounded-sm bg-white/10 border border-emerald-500/30" />
                    <span>Day with a memory</span>
                  </div>
                </GlassCard>
              </div>

              {/* Memory detail */}
              <div className="lg:col-span-2">
                {selectedDate ? (
                  <div className="space-y-4 slide-up">
                    <GlassCard className={selectedRealTracks?.length || selectedManual ? "border-emerald-500/20 bg-emerald-500/5" : ""}>
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <div className="text-[13px] text-white/40 mb-1">
                            {new Date(`${selectedDate}T00:00:00`).toLocaleDateString(undefined, { month: "long", day: "numeric", year: "numeric" })}
                          </div>
                          <h2 className="text-2xl font-black">
                            {selectedManual ? selectedManual.mood ?? "A day in your life." : selectedRealTracks?.length ? "A real day from your listening." : "Nothing here yet."}
                          </h2>
                        </div>
                        {selectedManual?.mood && <AuraBadge color="green">{selectedManual.mood}</AuraBadge>}
                      </div>
                      {selectedRealTracks?.length ? (
                        <div className="text-[12px] text-white/50">{selectedRealTracks.length} real track{selectedRealTracks.length === 1 ? "" : "s"} played</div>
                      ) : null}
                    </GlassCard>

                    {selectedRealTracks?.length ? (
                      <GlassCard>
                        <div className="text-[12px] text-white/40 font-bold uppercase mb-3 flex items-center gap-1.5"><Music size={13} /> What you listened to</div>
                        {selectedRealTracks.map((t, i) => (
                          <a
                            key={i}
                            href={t.external_url ?? "#"}
                            target="_blank"
                            rel="noreferrer"
                            className="flex items-center gap-3 py-2.5 border-b border-white/5 last:border-0 hover:bg-white/5 rounded-lg px-2 -mx-2 transition-colors"
                          >
                            {t.album_image ? (
                              // eslint-disable-next-line @next/next/no-img-element
                              <img src={t.album_image} alt="" className="w-8 h-8 rounded-lg object-cover shrink-0" />
                            ) : (
                              <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-emerald-400 shrink-0"><Play size={12} className="fill-current" /></div>
                            )}
                            <div className="flex-1 min-w-0">
                              <div className="text-[14px] text-white/80 font-medium truncate">{t.name}</div>
                              <div className="text-[11px] text-white/40 truncate">{t.artist}</div>
                            </div>
                            <span className="text-[11px] text-white/30 shrink-0">
                              {t.played_at ? new Date(t.played_at).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" }) : ""}
                            </span>
                          </a>
                        ))}
                      </GlassCard>
                    ) : null}

                    <GlassCard>
                      <div className="text-[12px] text-white/40 font-bold uppercase mb-3 flex items-center gap-1.5"><StickyNote size={13} /> Your note</div>
                      {editing ? (
                        <div className="space-y-3">
                          <textarea
                            value={noteDraft}
                            onChange={(e) => setNoteDraft(e.target.value)}
                            placeholder="What happened this day? What were you listening to, and why?"
                            rows={4}
                            maxLength={2000}
                            className="w-full px-3 py-2.5 bg-white/5 border border-white/10 rounded-xl text-[13px] placeholder:text-white/25 focus:outline-none focus:border-emerald-500/50 resize-none"
                          />
                          <div className="flex items-center gap-2 flex-wrap">
                            <select
                              value={moodDraft}
                              onChange={(e) => setMoodDraft(e.target.value)}
                              className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-[12px] text-white/80 focus:outline-none focus:border-emerald-500/50"
                            >
                              <option value="">No mood</option>
                              {MOODS.map((m) => <option key={m} value={m}>{m}</option>)}
                            </select>
                            <button
                              onClick={saveMemory}
                              disabled={saving || !noteDraft.trim()}
                              className="px-4 py-2 rounded-lg bg-emerald-500 text-black text-[12px] font-black hover:brightness-110 disabled:opacity-50 transition-all"
                            >
                              {saving ? "Saving…" : "Save memory"}
                            </button>
                            <button
                              onClick={() => setEditing(false)}
                              className="px-3 py-2 rounded-lg border border-white/10 text-white/60 text-[12px] font-bold hover:text-white inline-flex items-center gap-1"
                            >
                              <X size={12} /> Cancel
                            </button>
                          </div>
                        </div>
                      ) : selectedManual ? (
                        <div className="space-y-3">
                          <p className="text-[14px] text-white/70 italic leading-relaxed">&quot;{selectedManual.note}&quot;</p>
                          <div className="flex gap-2">
                            <button onClick={startEditing} className="px-3 py-1.5 rounded-lg border border-white/10 text-white/60 text-[12px] font-bold hover:text-white inline-flex items-center gap-1.5">
                              <Pencil size={11} /> Edit
                            </button>
                            <button onClick={deleteMemory} disabled={saving} className="px-3 py-1.5 rounded-lg border border-red-500/20 text-red-400 text-[12px] font-bold hover:bg-red-500/10 disabled:opacity-50 inline-flex items-center gap-1.5">
                              <Trash2 size={11} /> Delete
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={startEditing}
                          className="px-4 py-2.5 rounded-xl bg-emerald-500/15 text-emerald-300 text-[13px] font-bold hover:bg-emerald-500/25 transition-colors inline-flex items-center gap-1.5"
                        >
                          <Plus size={14} /> Add a memory for this day
                        </button>
                      )}
                    </GlassCard>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full glass-card py-20 text-center">
                    <Calendar size={40} className="text-white/20 mb-4" />
                    <p className="text-white/40 text-[14px]">Select a date to add or view a memory.</p>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
