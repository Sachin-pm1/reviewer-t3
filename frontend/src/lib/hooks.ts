/**
 * SWR data hooks — one per resource type.
 * All reads go through SWR for automatic caching, deduplication, and revalidation.
 */

import useSWR, { mutate as globalMutate } from "swr";
import { api } from "./api";

// Generic fetcher used by SWR. The key IS the fetch call itself (a thunk),
// so SWR's cache key is the function reference — stable per closure.
function thunkFetcher<T>(fn: () => Promise<T>) {
  return fn();
}

// --- Projects ---
export function useProjects() {
  return useSWR("projects", () => api.projects.list(), {
    revalidateOnFocus: false,
  });
}

export function useProject(id: string | null) {
  return useSWR(id ? `project/${id}` : null, () => api.projects.get(id!), {
    revalidateOnFocus: false,
  });
}

export function revalidateProjects() {
  return globalMutate("projects");
}

export function revalidateProject(id: string) {
  return globalMutate(`project/${id}`);
}

// --- Source types catalog ---
export function useSourceTypes() {
  return useSWR("source-types", () => api.sources.types(), {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  });
}

// --- Jobs ---
export function useJob(jobId: string | null, refreshIntervalMs = 0) {
  return useSWR(
    jobId ? `job/${jobId}` : null,
    () => api.jobs.get(jobId!),
    {
      refreshInterval: refreshIntervalMs,
      revalidateOnFocus: false,
    }
  );
}

// --- Reviews ---
export function useReviews(projectId: string | null, limit = 50) {
  return useSWR(
    projectId ? `reviews/${projectId}/${limit}` : null,
    () => api.reviews.list(projectId!, limit),
    { revalidateOnFocus: false }
  );
}

// --- Insights ---
export function useInsights(projectId: string | null) {
  return useSWR(
    projectId ? `insights/${projectId}` : null,
    () => api.insights.get(projectId!),
    { revalidateOnFocus: false }
  );
}

export function revalidateInsights(projectId: string) {
  return globalMutate(`insights/${projectId}`);
}

// --- Reports ---
export function useReports(projectId: string | null) {
  return useSWR(
    projectId ? `reports/${projectId}` : null,
    () => api.reports.list(projectId!),
    { revalidateOnFocus: false }
  );
}

export function useReportTypes() {
  return useSWR("report-types", () => api.reports.types(), {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  });
}

export function revalidateReports(projectId: string) {
  return globalMutate(`reports/${projectId}`);
}

// --- Health ---
export function useHealth() {
  return useSWR("health", () => api.health.get(), {
    refreshInterval: 30_000,
    revalidateOnFocus: false,
  });
}

export { thunkFetcher };
