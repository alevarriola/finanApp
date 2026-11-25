"use client";

import { useCallback, useSyncExternalStore } from "react";

// Fired on same-tab writes; the native "storage" event only covers other tabs.
const STORAGE_CHANGE_EVENT = "kash-storage-change";

function subscribe(onChange: () => void) {
  window.addEventListener("storage", onChange);
  window.addEventListener(STORAGE_CHANGE_EVENT, onChange);
  return () => {
    window.removeEventListener("storage", onChange);
    window.removeEventListener(STORAGE_CHANGE_EVENT, onChange);
  };
}

function readStorage(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

/**
 * A string choice persisted in localStorage (theme, locale...).
 * The server and the first client render use `fallback`, so hydration stays consistent.
 */
export function useStoredChoice<T extends string>(
  key: string,
  options: readonly T[],
  fallback: T,
) {
  const value = useSyncExternalStore(
    subscribe,
    () => {
      const stored = readStorage(key);
      return options.includes(stored as T) ? (stored as T) : fallback;
    },
    () => fallback,
  );

  const setValue = useCallback(
    (next: T) => {
      try {
        localStorage.setItem(key, next);
      } catch {
        // Storage can be unavailable (private mode); the choice just won't persist.
      }
      window.dispatchEvent(new Event(STORAGE_CHANGE_EVENT));
    },
    [key],
  );

  return [value, setValue] as const;
}
