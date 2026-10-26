import type {
  AuthResponse,
  CompanionReply,
  CompanionTurn,
  ExperienceTrackRequest,
  Memory,
  MemoryIn,
  SpotifyAuthorizeResponse,
  SpotifyOverview,
  SpotifyStatus,
  TasteProfile,
  TrackPick,
  User,
} from "./types";

const BASE = "/api";
export const TOKEN_KEY = "spotify-aura-token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) window.localStorage.setItem(TOKEN_KEY, token);
  else window.localStorage.removeItem(TOKEN_KEY);
}

export class ApiResponseError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiResponseError";
    this.status = status;
    this.code = code;
  }
}

async function req<T>(path: string, options: RequestInit = {}, auth = false): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }
  const res = await fetch(`${BASE}${path}`, {
    headers: { ...headers, ...options.headers },
    ...options,
  });

  if (!res.ok) {
    let code = "unknown_error";
    let message = res.statusText;
    try {
      const body = await res.json();
      code = body?.error?.code ?? code;
      message = body?.error?.message ?? message;
    } catch {
      // keep defaults
    }
    throw new ApiResponseError(res.status, code, message);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  companion: {
    chat: (message: string, history: CompanionTurn[], taste: TasteProfile) =>
      req<CompanionReply>("/companion/chat", {
        method: "POST",
        body: JSON.stringify({ message, history, taste }),
      }),
  },
  catalog: {
    experienceTrack: (payload: ExperienceTrackRequest) =>
      req<TrackPick>("/catalog/experience-track", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },
  auth: {
    signup: (email: string, password: string) =>
      req<AuthResponse>("/auth/signup", { method: "POST", body: JSON.stringify({ email, password }) }),
    signin: (email: string, password: string) =>
      req<AuthResponse>("/auth/signin", { method: "POST", body: JSON.stringify({ email, password }) }),
    me: () => req<User>("/auth/me", {}, true),
  },
  me: {
    getTaste: () => req<TasteProfile>("/me/taste", {}, true),
    setTaste: (payload: TasteProfile) =>
      req<TasteProfile>("/me/taste", { method: "PUT", body: JSON.stringify(payload) }, true),
  },
  spotifyConnect: {
    login: () => req<SpotifyAuthorizeResponse>("/auth/spotify/login", {}, true),
    status: () => req<SpotifyStatus>("/me/spotify/status", {}, true),
    overview: () => req<SpotifyOverview>("/me/spotify/overview", {}, true),
    disconnect: () => req<void>("/me/spotify/disconnect", { method: "POST" }, true),
  },
  memories: {
    list: () => req<Memory[]>("/me/memories", {}, true),
    upsert: (payload: MemoryIn) =>
      req<Memory>("/me/memories", { method: "POST", body: JSON.stringify(payload) }, true),
    remove: (id: string) => req<void>(`/me/memories/${id}`, { method: "DELETE" }, true),
  },
};
