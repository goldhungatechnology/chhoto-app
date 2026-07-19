"use client";

import { useState, useEffect, useCallback } from "react";
import { useTheme } from "next-themes";
import { useMe, useUpdateInterface } from "@/modules/auth/api/hooks";

export const useNavbar = () => {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const { data, isLoading } = useMe();
  const [searchQuery, setSearchQuery] = useState("");
  const [isCommandOpen, setIsCommandOpen] = useState(false);

  // Keyboard shortcut listener for ⌘K or Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsCommandOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const { updateInterfaceAsync } = useUpdateInterface();

  // Theme Toggle logic
  const toggleTheme = useCallback(() => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    if (data?.data?.user) {
      updateInterfaceAsync({ theme: nextTheme, language: "en" }).catch(() => {});
    }
  }, [theme, setTheme, data, updateInterfaceAsync]);

  // Sidebar toggle triggering a custom window event
  const toggleSidebar = useCallback(() => {
    if (typeof window !== "undefined") {
      const event = new CustomEvent("toggle-sidebar");
      window.dispatchEvent(event);
    }
  }, []);

  return {
    theme: theme,
    resolvedTheme: resolvedTheme || "light",
    toggleTheme,
    searchQuery,
    setSearchQuery,
    isCommandOpen,
    setIsCommandOpen,
    toggleSidebar,
    user: data?.data?.user,
    userLoading: isLoading,
  };
};
