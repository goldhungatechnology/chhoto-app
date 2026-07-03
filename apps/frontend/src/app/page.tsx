import Link from "next/link";

import { ROUTES } from "@/core/config";
import { APP_NAME } from "@/core/config";

// ----------------------------------------------------------------------

export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex flex-1 w-full max-w-lg flex-col items-center justify-center gap-8 py-32 px-8">
        <h1 className="text-4xl font-bold tracking-tight text-slate-900 dark:text-zinc-50">
          {APP_NAME}
        </h1>
        <p className="text-center text-lg text-zinc-600 dark:text-zinc-400">
          Welcome to {APP_NAME}. Get started by logging in or creating an
          account.
        </p>
        <div className="flex gap-4">
          <Link
            href={ROUTES.AUTH.LOGIN}
            className="flex h-11 items-center justify-center rounded-full bg-slate-900 px-6 text-sm font-semibold text-white transition-colors hover:bg-slate-800"
          >
            Login
          </Link>
          <Link
            href={ROUTES.AUTH.REGISTER}
            className="flex h-11 items-center justify-center rounded-full border border-slate-300 px-6 text-sm font-semibold text-slate-900 transition-colors hover:bg-slate-100"
          >
            Register
          </Link>
        </div>
      </main>
    </div>
  );
}
