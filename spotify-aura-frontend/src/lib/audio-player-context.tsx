"use client";

/**
 * One shared <audio> element + queue for every "play preview" button in the
 * app, instead of each page spawning its own throwaway `new Audio(url)`
 * (the pre-existing pattern in Discovery/Commute/Soundtrack never actually
 * paused anything — toggling "off" just relabeled the button while the old
 * Audio instance kept playing in the background until its own 30s clip
 * ended). Mounted once in layout-shell.tsx so playback and the mini-player
 * persist across page navigation.
 */

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";

export interface PlayerTrack {
  id: string;
  name: string;
  artist: string;
  artworkUrl: string | null;
  previewUrl: string;
  externalUrl: string | null;
}

interface AudioPlayerValue {
  queue: PlayerTrack[];
  index: number;
  current: PlayerTrack | null;
  playing: boolean;
  volume: number;
  progress: number;
  duration: number;
  playQueue: (tracks: PlayerTrack[], startIndex: number) => void;
  toggle: () => void;
  next: () => void;
  prev: () => void;
  setVolume: (value: number) => void;
  seek: (fraction: number) => void;
  close: () => void;
}

const AudioPlayerContext = createContext<AudioPlayerValue | null>(null);

export function AudioPlayerProvider({ children }: { children: React.ReactNode }) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  if (audioRef.current === null && typeof window !== "undefined") {
    audioRef.current = new Audio();
  }

  const [queue, setQueue] = useState<PlayerTrack[]>([]);
  const [index, setIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [volume, setVolumeState] = useState(0.8);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  const queueRef = useRef(queue);
  const indexRef = useRef(index);
  queueRef.current = queue;
  indexRef.current = index;

  const loadAndPlay = useCallback((i: number) => {
    const audio = audioRef.current;
    const track = queueRef.current[i];
    if (!audio || !track) return;
    setIndex(i);
    audio.src = track.previewUrl;
    audio.currentTime = 0;
    audio.play().catch(() => {});
  }, []);

  const next = useCallback(() => {
    const q = queueRef.current;
    if (q.length === 0) return;
    loadAndPlay((indexRef.current + 1) % q.length);
  }, [loadAndPlay]);

  const prev = useCallback(() => {
    const q = queueRef.current;
    if (q.length === 0) return;
    loadAndPlay((indexRef.current - 1 + q.length) % q.length);
  }, [loadAndPlay]);

  // Register DOM listeners once — `next` is stable (loadAndPlay has no deps).
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const onTime = () => setProgress(audio.currentTime);
    const onLoaded = () => setDuration(audio.duration || 0);
    const onPlay = () => setPlaying(true);
    const onPause = () => setPlaying(false);
    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("loadedmetadata", onLoaded);
    audio.addEventListener("ended", next);
    audio.addEventListener("play", onPlay);
    audio.addEventListener("pause", onPause);
    return () => {
      audio.removeEventListener("timeupdate", onTime);
      audio.removeEventListener("loadedmetadata", onLoaded);
      audio.removeEventListener("ended", next);
      audio.removeEventListener("play", onPlay);
      audio.removeEventListener("pause", onPause);
    };
  }, [next]);

  useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume;
  }, [volume]);

  const playQueue = useCallback((tracks: PlayerTrack[], startIndex: number) => {
    queueRef.current = tracks;
    setQueue(tracks);
    loadAndPlay(startIndex);
  }, [loadAndPlay]);

  const toggle = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    if (audio.paused) {
      if (audio.src) audio.play().catch(() => {});
      else if (queueRef.current[indexRef.current]) loadAndPlay(indexRef.current);
    } else {
      audio.pause();
    }
  }, [loadAndPlay]);

  const seek = useCallback((fraction: number) => {
    const audio = audioRef.current;
    if (!audio || !duration) return;
    audio.currentTime = fraction * duration;
  }, [duration]);

  const close = useCallback(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.pause();
      audio.removeAttribute("src");
    }
    queueRef.current = [];
    setQueue([]);
    setIndex(0);
    setProgress(0);
    setDuration(0);
  }, []);

  const value: AudioPlayerValue = {
    queue,
    index,
    current: queue[index] ?? null,
    playing,
    volume,
    progress,
    duration,
    playQueue,
    toggle,
    next,
    prev,
    setVolume: setVolumeState,
    seek,
    close,
  };

  return <AudioPlayerContext.Provider value={value}>{children}</AudioPlayerContext.Provider>;
}

export function useAudioPlayer(): AudioPlayerValue {
  const ctx = useContext(AudioPlayerContext);
  if (!ctx) throw new Error("useAudioPlayer must be used within AudioPlayerProvider");
  return ctx;
}
