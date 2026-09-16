const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001/api/v1";

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window === "undefined" ? null : sessionStorage.getItem("access_token");
  const response = await fetch(`${apiUrl}${path}`, { ...options, headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers } });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    if (response.status === 401 && typeof window !== "undefined") {
      sessionStorage.removeItem("access_token");
      throw new Error("Your session has expired. Please sign in again.");
    }
    throw new Error(body.detail ?? "Request failed");
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
