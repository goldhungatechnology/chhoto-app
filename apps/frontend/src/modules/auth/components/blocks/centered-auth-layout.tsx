import { ReactNode } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

// ----------------------------------------------------------------------

interface CenteredAuthLayoutProps {
  children: ReactNode;
  backHref?: string;
  backLabel?: string;
}

// ----------------------------------------------------------------------

export default function CenteredAuthLayout({
  children,
  backHref,
  backLabel = "Back",
}: CenteredAuthLayoutProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50/60 px-4">
      <div className="w-full max-w-[440px] space-y-5">
        {backHref && (
          <Link
            href={backHref}
            className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft size={14} />
            {backLabel}
          </Link>
        )}

        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8">
          <div className="flex flex-col gap-6">{children}</div>
        </div>
      </div>
    </div>
  );
}
