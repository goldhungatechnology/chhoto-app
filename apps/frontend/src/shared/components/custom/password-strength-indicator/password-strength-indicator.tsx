import { usePasswordStrength } from "@/shared/hooks/use-password-strength";
import { cn } from "@/shared/lib/utils";

const strengthColors: Record<string, string> = {
  weak: "bg-red-500",
  medium: "bg-yellow-500",
  strong: "bg-green-500",
};

function StrengthBar({ strength }: { strength: string | null }) {
  if (!strength) return null;

  const segments = { weak: 1, medium: 2, strong: 3 };
  const total = 3;
  const filled = segments[strength as keyof typeof segments] ?? 0;

  return (
    <div className="flex gap-1">
      {Array.from({ length: total }).map((_, i) => (
        <div
          key={i}
          className={cn(
            "h-1 flex-1 rounded-full transition-colors",
            i < filled ? strengthColors[strength] : "bg-muted",
          )}
        />
      ))}
    </div>
  );
}

function Requirements({ requirements }: { requirements: Array<{ label: string; met: boolean }> }) {
  return (
    <ul className="flex flex-col gap-1">
      {requirements.map((req, i) => (
        <li key={i} className={cn("text-xs", req.met ? "text-green-600" : "text-muted-foreground")}>
          {req.met ? "✓" : "○"} {req.label}
        </li>
      ))}
    </ul>
  );
}

export default function PasswordStrengthIndicator() {
  const result = usePasswordStrength();

  return (
    <div className="flex flex-col gap-2">
      {result && (
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium capitalize">{result.label}</span>
        </div>
      )}
      <StrengthBar strength={result?.strength ?? null} />
      {result && <Requirements requirements={result.requirements} />}
    </div>
  );
}
