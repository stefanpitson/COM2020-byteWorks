const IMAGE_BASE = import.meta.env.DEV
  ? "http://localhost:8000"
  : "";

export function resolveImageUrl(path?: string | null) {
  if (!path) return null;
  return `${IMAGE_BASE}${path}`;
}