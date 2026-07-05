import Link from "next/link";
import Image from "next/image";
import { APP_NAME } from "@/core/config";

interface LogoProps {
  className?: string;
  titleClassName?: string;
}

export function Logo({ className }: LogoProps) {
  return (
    <Link href="/" className={className}>
      <Image
        src="/assets/logo/chhoto-logo.png"
        alt={APP_NAME}
        width={150}
        height={40}
        priority
        className="object-contain object-left"
      />
    </Link>
  );
}
