/**
 * Centralized API configuration for Agentic Research PRO.
 *
 * Handles URL construction for both single-origin deployments (local dev / Docker)
 * and split production deployments (Vercel Frontend + Render Backend).
 */

// Normalized base URL without trailing slash (e.g., "https://agentic-research.onrender.com")
export const API_BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL || ''
).trim().replace(/\/+$/, '');

/**
 * Constructs a fully qualified or relative API URL from a given endpoint path or stream URL.
 *
 * Safety guarantees:
 * - If `path` is already an absolute URL (starts with http:// or https://), returns it unchanged.
 * - If `path` is a relative path (e.g., "/api/research"), prepends API_BASE_URL without duplicate slashes.
 * - If API_BASE_URL is empty, preserves the relative path unchanged for same-origin / Vite proxy usage.
 * - Fully preserves query parameters and fragments.
 *
 * @param path - Relative endpoint path (e.g. "/api/research") or absolute URL.
 * @returns Safe, normalized URL for fetch, EventSource, or anchor links.
 */
export function getApiUrl(path: string): string {
  if (!path) {
    return API_BASE_URL;
  }

  // If already an absolute URL, do not double-prefix
  if (/^https?:\/\//i.test(path)) {
    return path;
  }

  // Ensure leading slash on relative path
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;

  // If no base URL is configured, return the relative path (preserves dev proxy & same-origin)
  if (!API_BASE_URL) {
    return normalizedPath;
  }

  return `${API_BASE_URL}${normalizedPath}`;
}
