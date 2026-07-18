import Link from "next/link";
import Image from "next/image";
import clsx from "clsx";

interface LogoProps {
  className?: string;
  variant?: "sm" | "md" | "lg";
}

export function Logo({ className, variant = "md" }: LogoProps) {
  const sizes = {
    sm: "w-8 h-8", // 32x32
    md: "w-25 h-12", // 48x48
    lg: "w-40 h-16", // 64x64
  };

  return (
    <Link href="/" className={clsx("inline-block", sizes[variant], className)}>
      <Image
        src="/assets/logo/chhoto-logo.png"
        alt="Logo"
        width={160}
        height={64}
        className="w-full h-full object-contain"
        unoptimized
      />
    </Link>
  );
}
