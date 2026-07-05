import { Sun, Moon, Check, ArrowRight } from "lucide-react";
import { Button } from "@/shared/components/ui/button";

interface StepThemeProps {
  theme: "light" | "dark" | "";
  setTheme: (theme: "light" | "dark" | "") => void;
  onContinue: () => void;
  onSkip: () => void;
}

export default function StepTheme({
  theme,
  setTheme,
  onContinue,
  onSkip,
}: StepThemeProps) {
  const isValid = theme === "light" || theme === "dark";

  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 md:text-3xl">
          Choose your theme
        </h1>
        <p className="text-[15px] text-slate-500">
          Select your theme preference. You can always change this later.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Light Theme Option */}
        <button
          onClick={() => setTheme("light")}
          className={`relative flex flex-col items-center gap-3 rounded-2xl border p-6 transition-all duration-300 cursor-pointer ${
            theme === "light"
              ? "border-primary bg-primary-soft/30 ring-1 ring-primary"
              : "border-slate-200 bg-white hover:border-slate-350"
          }`}
        >
          <div
            className={`flex h-12 w-12 items-center justify-center rounded-xl transition-colors duration-200 ${
              theme === "light"
                ? "bg-primary text-white"
                : "bg-slate-50 text-slate-500"
            }`}
          >
            <Sun size={24} />
          </div>
          <span className="font-semibold text-slate-800">Light</span>
          {theme === "light" && (
            <div className="absolute top-3 right-3 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-white">
              <Check size={12} strokeWidth={3} />
            </div>
          )}
        </button>

        {/* Dark Theme Option */}
        <button
          onClick={() => setTheme("dark")}
          className={`relative flex flex-col items-center gap-3 rounded-2xl border p-6 transition-all duration-300 cursor-pointer ${
            theme === "dark"
              ? "border-primary bg-primary-soft/30 ring-1 ring-primary"
              : "border-slate-200 bg-white hover:border-slate-350"
          }`}
        >
          <div
            className={`flex h-12 w-12 items-center justify-center rounded-xl transition-colors duration-200 ${
              theme === "dark"
                ? "bg-primary text-white"
                : "bg-slate-50 text-slate-500"
            }`}
          >
            <Moon size={24} />
          </div>
          <span className="font-semibold text-slate-800">Dark</span>
          {theme === "dark" && (
            <div className="absolute top-3 right-3 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-white">
              <Check size={12} strokeWidth={3} />
            </div>
          )}
        </button>
      </div>

      <div className="flex flex-col gap-3">
        <Button
          onClick={onContinue}
          disabled={!isValid}
          className={`h-12 w-full rounded-full text-[15px] font-semibold text-white shadow-none transition-all duration-300 ${
            isValid
              ? "bg-primary hover:bg-primary-hover hover:shadow-lg cursor-pointer"
              : "bg-slate-200/80 text-slate-400 opacity-25 cursor-not-allowed pointer-events-none"
          }`}
        >
          Continue
        </Button>

        <button
          onClick={onSkip}
          className="flex items-center justify-center gap-1.5 py-2 text-sm font-semibold text-slate-500 hover:text-slate-900 transition-colors duration-200 cursor-pointer self-center"
        >
          Skip for now <ArrowRight size={14} />
        </button>
      </div>
    </div>
  );
}
