"use client";

import { CreateLinkSection } from "../components/sections/create-link-section";

export default function CreateLinkView() {
  return (
    <div className="flex flex-col flex-1 items-center bg-zinc-50/50 dark:bg-black/50 font-sans w-full min-h-[calc(100vh-64px)]">
      <main className="flex flex-col w-full items-center justify-start gap-8 py-8 px-4 md:px-8 max-w-7xl">
        <div className="flex flex-col items-center text-center gap-2 max-w-lg">
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-zinc-50 md:text-4xl bg-gradient-brand bg-clip-text text-transparent">
            Shorten Your Links
          </h1>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Create clean, trackable short URLs and dynamic QR codes in seconds.
          </p>
        </div>

        <CreateLinkSection />
      </main>
    </div>
  );
}
