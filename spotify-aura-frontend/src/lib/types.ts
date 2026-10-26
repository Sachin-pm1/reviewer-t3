export interface TasteProfile {
  seed_artists: string[];
  seed_genres: string[];
  novelty: number; // 0 = stay close to known taste, 100 = maximum stretch
}

export interface CompanionTurn {
  role: "user" | "aura";
  text: string;
}

export interface TrackPick {
  artist: string;
  track: string;
  why: string;
  novelty_score: number;
  artwork_url: string | null;
  preview_url: string | null;
  external_url: string | null;
  source: "spotify" | "itunes" | null;
}

export interface Journey {
  mood: string;
  reasoning: string;
  energy: number;
  picks: TrackPick[];
}

export interface CompanionReply {
  reply: string;
  journey: Journey | null;
}

export interface ExperienceTrackRequest {
  title: string;
  mood: string;
  desc: string;
}

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SpotifyAuthorizeResponse {
  authorize_url: string;
}

export interface SpotifyStatus {
  connected: boolean;
  display_name: string | null;
  spotify_user_id: string | null;
  connected_at: string | null;
}

export interface SpotifyArtist {
  name: string;
  genres: string[];
  image_url: string | null;
  external_url: string | null;
  popularity: number | null;
}

export interface SpotifyRealTrack {
  name: string;
  artist: string;
  album_image: string | null;
  external_url: string | null;
  preview_url: string | null;
  popularity: number | null;
  played_at: string | null;
}

export interface SpotifyOverview {
  connected: boolean;
  display_name: string | null;
  product: string | null;
  top_artists: SpotifyArtist[];
  top_tracks: SpotifyRealTrack[];
  recently_played: SpotifyRealTrack[];
  top_genres: string[];
}

export interface MemoryIn {
  date: string; // "YYYY-MM-DD"
  note: string;
  mood?: string | null;
}

export interface Memory {
  id: string;
  date: string;
  note: string;
  mood: string | null;
  created_at: string;
}
