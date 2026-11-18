import { ShortenURLResponse, URLHistoryItem } from "../types";

const HISTORY_STORAGE_KEY = "url_shortener_history";

export const getStoredLinks = (): URLHistoryItem[] => {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(HISTORY_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (err) {
    console.error("Failed to read URL history from localStorage", err);
    return [];
  }
};

export const saveLinkToHistory = (item: ShortenURLResponse): URLHistoryItem[] => {
  if (typeof window === "undefined") return [];
  try {
    const existing = getStoredLinks();
    // Avoid duplicates by short_code
    const filtered = existing.filter((link) => link.short_code !== item.short_code);
    const updated: URLHistoryItem[] = [
      {
        ...item,
        created_at: item.created_at || new Date().toISOString(),
      },
      ...filtered,
    ];
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(updated));
    return updated;
  } catch (err) {
    console.error("Failed to save URL to history", err);
    return [];
  }
};

export const removeLinkFromHistory = (shortCode: string): URLHistoryItem[] => {
  if (typeof window === "undefined") return [];
  try {
    const existing = getStoredLinks();
    const updated = existing.filter((item) => item.short_code !== shortCode);
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(updated));
    return updated;
  } catch (err) {
    console.error("Failed to remove URL from history", err);
    return [];
  }
};

export const clearLinkHistory = (): void => {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(HISTORY_STORAGE_KEY);
  } catch (err) {
    console.error("Failed to clear URL history", err);
  }
};
