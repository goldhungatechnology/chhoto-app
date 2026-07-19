import { Button } from "@/shared/components/ui/button";

interface StepNameProps {
  fullName: string;
  setFullName: (name: string) => void;
  onContinue: () => void;
}

export default function StepName({
  fullName,
  setFullName,
  onContinue,
}: StepNameProps) {
  const isValid = fullName.trim().length > 0;

  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 md:text-3xl dark:text-white">
          What&apos;s your name?
        </h1>
        <p className="text-[15px] text-slate-500 dark:text-slate-400">
          Enter your full name as you&apos;d like it to appear on your account.
        </p>
      </div>

      <div className="relative">
        <input
          type="text"
          placeholder="John Doe"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="h-12 w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 py-3 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary shadow-sm transition-all duration-200"
          autoFocus
        />
      </div>

      <Button
        onClick={onContinue}
        disabled={!isValid}
        className={`h-12 w-full rounded-full text-[15px] font-semibold text-white shadow-none transition-all duration-300 ${
          isValid
            ? "bg-primary hover:bg-primary-hover hover:shadow-lg cursor-pointer"
            : "bg-slate-200/80 dark:bg-slate-800/80 text-slate-400 dark:text-slate-600 opacity-25 cursor-not-allowed pointer-events-none"
        }`}
      >
        Continue
      </Button>
    </div>
  );
}
