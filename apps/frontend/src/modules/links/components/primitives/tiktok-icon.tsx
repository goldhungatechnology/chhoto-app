import { cn } from "@/lib/utils";

export function TiktokIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={cn("text-[#00f2fe] dark:text-[#fe0979]", className)}
    >
      <path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5-5" />
    </svg>
  );
}
