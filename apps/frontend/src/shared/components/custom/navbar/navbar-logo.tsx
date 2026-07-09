"use client";

import Link from "next/link";

interface NavbarLogoProps {
  className?: string;
}

export function NavbarLogo({ className }: NavbarLogoProps) {
  return (
    <Link href="/" className={`flex items-center gap-2.5 group ${className || ""}`}>
      <div className="relative flex items-center justify-center w-8 h-8 rounded-xl bg-gradient-to-tr from-primary to-primary-light shadow-md shadow-primary/20 transition-all duration-300 group-hover:scale-105">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="w-4.5 h-4.5 text-white"
        >
          <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10M17 9.5c0-1.4-1.1-2.5-2.5-2.5H10.5C9.1 7 8 8.1 8 9.5s1.1 2.5 2.5 2.5h3c1.4 0 2.5 1.1 2.5 2.5s-1.1 2.5-2.5 2.5H9.5c-1.4 0-2.5-1.1-2.5-2.5" />
        </svg>
      </div>
      <span className="text-xl font-bold tracking-tight text-foreground transition-colors duration-200 group-hover:text-primary">
        Sellora
      </span>
    </Link>
  );
}
