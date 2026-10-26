import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatRelative(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export function sentimentColor(s: string) {
  switch (s) {
    case "positive": return "#34d399";
    case "negative": return "#f87171";
    case "mixed":    return "#fbbf24";
    default:         return "#9aa3b2";
  }
}

export function stars(rating: number | null) {
  if (rating == null) return null;
  const full = Math.round(rating);
  return "★".repeat(full) + "☆".repeat(Math.max(0, 5 - full));
}

export function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function pct(n: number) {
  return `${Math.round(n * 100)}%`;
}

/** Default JSON config templates shown in the Add Source form. */
export const SOURCE_TEMPLATES: Record<string, Record<string, unknown>> = {
  file_csv: {
    path: "data/sample_spotify_reviews.csv",
    text_column: "text",
    rating_column: "rating",
    id_column: "id",
  },
  google_play: {
    app_id: "com.spotify.music",
    count: 200,
    lang: "en",
    country: "us",
  },
  app_store: {
    app_id: "324684580",
    country: "us",
    max_pages: 5,
  },
  reddit: {
    query: "spotify discover new music",
    subreddit: "spotify",
    limit: 100,
    sort: "relevance",
    time_filter: "year",
  },
};
