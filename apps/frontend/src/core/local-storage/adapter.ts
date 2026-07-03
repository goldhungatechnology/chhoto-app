interface StorageOptions {
  expiryDays?: number;
}

interface StorageItem<T> {
  value: T;
  expiresAt?: number;
}

class LocalStorageAdapter {
  private isAvailable(): boolean {
    try {
      if (typeof window === "undefined") return false;
      const test = "__storage_test__";
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      return true;
    } catch {
      return false;
    }
  }

  setItem<T>(key: string, value: T, options?: StorageOptions): void {
    if (!this.isAvailable()) {
      console.warn("localStorage is not available");
      return;
    }

    try {
      const item: StorageItem<T> = {
        value,
        ...(options?.expiryDays && {
          expiresAt: Date.now() + options.expiryDays * 24 * 60 * 60 * 1000,
        }),
      };

      localStorage.setItem(key, JSON.stringify(item));
    } catch (error) {
      console.error(`Failed to set localStorage item "${key}":`, error);
    }
  }

  getItem<T>(key: string): T | null {
    if (!this.isAvailable()) {
      console.warn("localStorage is not available");
      return null;
    }

    try {
      const stored = localStorage.getItem(key);

      if (!stored) {
        return null;
      }

      const item: StorageItem<T> = JSON.parse(stored);

      // Check if item has expired
      if (item.expiresAt && Date.now() > item.expiresAt) {
        this.removeItem(key);
        return null;
      }

      return item.value;
    } catch (error) {
      console.error(`Failed to get localStorage item "${key}":`, error);
      return null;
    }
  }

  removeItem(key: string): void {
    if (!this.isAvailable()) {
      console.warn("localStorage is not available");
      return;
    }

    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error(`Failed to remove localStorage item "${key}":`, error);
    }
  }

  clear(): void {
    if (!this.isAvailable()) {
      console.warn("localStorage is not available");
      return;
    }

    try {
      localStorage.clear();
    } catch (error) {
      console.error("Failed to clear localStorage:", error);
    }
  }
}

export const localStorageAdapter = new LocalStorageAdapter();
