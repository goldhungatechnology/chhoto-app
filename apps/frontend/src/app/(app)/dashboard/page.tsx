import Link from "next/link";
import { Button } from "@/shared/components/ui/button";
import { Link2, Sparkles, BarChart3 } from "lucide-react";

export default function Dashboard() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50/30 font-sans dark:bg-black/30 py-16 px-6 md:px-12">
      <main className="flex flex-col w-full max-w-3xl items-center text-center gap-10">
        <div className="space-y-4">
          <div className="mx-auto flex items-center justify-center size-12 rounded-2xl bg-primary-soft/20 text-primary border border-primary-border/20 shadow-sm">
            <Sparkles className="size-6 fill-primary/10" />
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-zinc-50 sm:text-5xl">
            Welcome to{" "}
            <span className="bg-primary text-background">Chhoto</span>
          </h1>
          <p className="text-base text-zinc-600 dark:text-zinc-400 max-w-md mx-auto">
            Your premium, self-hosted link management platform. Create short
            links, track metrics, and generate QR codes.
          </p>
        </div>

        {/* Quick action grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full mt-4">
          <div className="flex flex-col items-center justify-between gap-4 p-6 bg-card border border-border/60 rounded-3xl text-center shadow-md">
            <div className="p-3 bg-primary-soft/10 text-primary rounded-2xl">
              <Link2 className="size-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-sm text-foreground">
                Shorten Links
              </h3>
              <p className="text-xs text-muted-foreground">
                Create trackable, branded custom links.
              </p>
            </div>
            <Button size="sm" className="rounded-xl mt-2 w-full" asChild>
              <Link href="/links">Go to Links</Link>
            </Button>
          </div>

          <div className="flex flex-col items-center justify-between gap-4 p-6 bg-card border border-border/60 rounded-3xl text-center shadow-md">
            <div className="p-3 bg-primary-soft/10 text-primary rounded-2xl">
              <BarChart3 className="size-6" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-sm text-foreground">
                View Analytics
              </h3>
              <p className="text-xs text-muted-foreground">
                Analyze clicks, devices, and countries.
              </p>
            </div>
            <Button
              size="sm"
              variant="outline"
              className="rounded-xl mt-2 w-full"
              asChild
            >
              <Link href="/analytics">Analytics</Link>
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
