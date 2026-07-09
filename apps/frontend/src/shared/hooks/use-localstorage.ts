import { useCallback } from "react";

export default function useLocalStorage() {
  const setItem = useCallback((key: string, value: string) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error("Failed to save to localStorage:", error);
    }
  }, []);

  const getItem = useCallback((key: string) => {
    try {
      const value = localStorage.getItem(key);

      if (value === null) return null;

      return JSON.parse(value);
    } catch (error) {
      console.error("Failed to read from localStorage:", error);
      return null;
    }
  }, []);

  const removeItem = useCallback((key: string) => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error("Failed to remove from localStorage:", error);
    }
  }, []);

  const clear = useCallback(() => {
    try {
      localStorage.clear();
    } catch (error) {
      console.error("Failed to clear localStorage:", error);
    }
  }, []);

  return {
    setItem,
    getItem,
    removeItem,
    clear,
  };
}
