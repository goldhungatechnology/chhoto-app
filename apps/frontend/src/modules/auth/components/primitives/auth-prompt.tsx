import Link from "next/link";

import { Button } from "@/shared/components/ui/button";

// ----------------------------------------------------------------------

interface AuthPromptProps {
  content: string;
  title: string;
  href: string;
}

// ----------------------------------------------------------------------

export default function AuthPrompt({ content, title, href }: AuthPromptProps) {
  return (
    <div className="flex items-center justify-end gap-3 rounded-full border border-slate-200/70 bg-white/60 px-4 py-3 text-slate-800 backdrop-blur-sm">
      <p className="text-sm text-white/60">{content}</p>

      <Button
        asChild
        variant="link"
        className="h-auto rounded-none p-0 text-white underline-offset-4 hover:cursor-pointer hover:text-white hover:underline"
      >
        <Link href={href}>{title}</Link>
      </Button>
    </div>
  );
}
