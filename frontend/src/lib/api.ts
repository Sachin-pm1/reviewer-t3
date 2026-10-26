/**
 * Typed API client.
 *
 * All paths are prefixed with /api which Next.js rewrites to the FastAPI
 * backend via next.config.ts. This means the browser always talks to the
 * same origin (no CORS) and the API URL is a single config point.
 */

import type {
  ChatHistoryItem,
  ChatResponse,
  InsightsOverview,
  JobRead,
  ProjectDetail,
  ProjectRead,
  ReportRead,
  ReportSummary,
  ReviewRead,
  SourceRead,
} from "./types";

const BASE = "/api";

class ApiResponseError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiResponseError";
    this.status = status;
    this.code = code;
  }
}

async function req<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
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

// --- Projects ---

export const api = {
  projects: {
    list: () => req<ProjectRead[]>("/projects"),
    get: (id: string) => req<ProjectDetail>(`/projects/${id}`),
    create: (payload: { name: string; product_name: string; description?: string }) =>
      req<ProjectDetail>("/projects", { method: "POST", body: JSON.stringify(payload) }),
  },

  sources: {
    list: (projectId: string) => req<SourceRead[]>(`/projects/${projectId}/sources`),
    add: (projectId: string, payload: { source_type: string; config: Record<string, unknown> }) =>
      req<SourceRead>(`/projects/${projectId}/sources`, {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    types: () => req<string[]>("/source-types"),
  },

  jobs: {
    start: (projectId: string, options?: { max_reviews_per_source?: number }) =>
      req<JobRead>(`/projects/${projectId}/analyze`, {
        method: "POST",
        body: JSON.stringify(options ?? {}),
      }),
    get: (jobId: string) => req<JobRead>(`/jobs/${jobId}`),
  },

  reviews: {
    list: (projectId: string, limit = 50) =>
      req<ReviewRead[]>(`/projects/${projectId}/reviews?limit=${limit}`),
  },

  insights: {
    get: (projectId: string) => req<InsightsOverview>(`/projects/${projectId}/insights`),
  },

  chat: {
    ask: (projectId: string, question: string, top_k = 6) =>
      req<ChatResponse>(`/projects/${projectId}/chat`, {
        method: "POST",
        body: JSON.stringify({ question, top_k }),
      }),
    history: (projectId: string) =>
      req<ChatHistoryItem[]>(`/projects/${projectId}/chat`),
  },

  reports: {
    list: (projectId: string) => req<ReportSummary[]>(`/projects/${projectId}/reports`),
    generate: (projectId: string, report_type: string) =>
      req<ReportRead>(`/projects/${projectId}/reports`, {
        method: "POST",
        body: JSON.stringify({ report_type }),
      }),
    get: (reportId: string) => req<ReportRead>(`/reports/${reportId}`),
    types: () => req<string[]>("/report-types"),
  },

  health: {
    get: () => req<{ status: string; ai_enabled: boolean; model: string }>("/health"),
  },
};

export { ApiResponseError };
