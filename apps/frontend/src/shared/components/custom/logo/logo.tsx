import Link from "next/link";
import { APP_NAME } from "@/core/config";
import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  titleClassName?: string;
}

export function Logo({ className, titleClassName }: LogoProps) {
  return (
    <Link href="/" className={className}>
      <h1
        className={cn(
          "text-xl font-semibold tracking-tight text-primary",
          titleClassName,
        )}
      >
        {APP_NAME}
      </h1>
    </Link>
  );
}
