import { ReactNode } from "react";

import { Logo } from "@/shared/components/custom/logo";

import { InfoPanel } from "../primitives";

// ----------------------------------------------------------------------

interface AuthPromptConfig {
  content: string;
  title: string;
  href: string;
}

interface LoginRegisterLayoutProps {
  prompt?: AuthPromptConfig;
  children: ReactNode;
  footerContent?: ReactNode;
}

// ----------------------------------------------------------------------

export default function LoginRegisterLayout({
  children,
  footerContent,
}: LoginRegisterLayoutProps) {
  return (
    <div className="min-h-screen bg-white text-slate-900 md:grid md:grid-cols-2">
      <section className="relative flex min-h-screen flex-col overflow-hidden bg-white px-6 py-6 sm:px-8 lg:px-12">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(15,23,42,0.04),transparent_38%),radial-gradient(circle_at_bottom,rgba(15,23,42,0.02),transparent_28%)]" />

        <div className="relative z-10 flex items-center justify-center">
          <Logo variant="lg" />
        </div>

        <div className="relative flex flex-1 items-center py-8 sm:py-10">
          <div className="mx-auto flex w-full max-w-[400px] flex-col gap-7 text-center">
            <div className="space-y-7">{children}</div>

            {footerContent}

            <div className="w-full space-y-4 pt-2 text-center text-slate-500">
              <p className="text-sm text-slate-500">Trusted by teams at</p>

              <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-3">
                <span className="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <span className="h-3 w-3 rounded-full bg-slate-400" />
                  headspace
                </span>
                <span className="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <span className="h-3 w-3 rounded-full border border-slate-400" />
                  airbnb
                </span>
                <span className="text-sm font-medium text-slate-700">
                  Revolut
                </span>
                <span className="text-sm font-medium text-slate-700">
                  duolingo
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <InfoPanel className="hidden md:block" />
    </div>
  );
}
