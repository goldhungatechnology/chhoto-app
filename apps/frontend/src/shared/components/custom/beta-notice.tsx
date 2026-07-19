"use client";

import { useState, useEffect } from "react";
import { AlertTriangle, X } from "lucide-react";

export function BetaNotice() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Check if the user has already dismissed the beta notice
    const isDismissed = localStorage.getItem("chhoto_beta_notice_dismissed");
    if (!isDismissed) {
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, 0);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleDismiss = () => {
    setIsVisible(false);
    localStorage.setItem("chhoto_beta_notice_dismissed", "true");
  };

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-xs sm:max-w-sm rounded-2xl border border-amber-500/20 dark:border-amber-500/30 bg-amber-50/90 dark:bg-amber-950/45 p-4 shadow-lg backdrop-blur-md flex gap-3 animate-in fade-in slide-in-from-bottom-5 duration-500 hover:shadow-xl transition-all">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400">
        <AlertTriangle size={18} />
      </div>

      <div className="flex-1 pr-4">
        <h4 className="text-sm font-semibold text-amber-900 dark:text-amber-200">
          Beta Version
        </h4>
        <p className="mt-1 text-xs text-amber-700/90 dark:text-amber-300/80 leading-relaxed">
          Chhoto is currently in beta. You may encounter bugs or experience unfinished features.
        </p>
      </div>

      <button
        onClick={handleDismiss}
        className="absolute top-3 right-3 text-amber-800/60 hover:text-amber-900 dark:text-amber-400/60 dark:hover:text-amber-200 transition-colors p-1 rounded-lg hover:bg-amber-100/50 dark:hover:bg-amber-900/30 cursor-pointer"
        aria-label="Close alert"
      >
        <X size={14} />
      </button>
    </div>
  );
}
