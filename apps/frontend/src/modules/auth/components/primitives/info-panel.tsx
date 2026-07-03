import { cn } from "@/lib/utils";

// ----------------------------------------------------------------------

interface InfoPanelProps {
  className?: string;
}

// ----------------------------------------------------------------------

export default function InfoPanel({ className }: InfoPanelProps) {
  const tiles = [
    {
      className:
        "left-[5%] top-[4%] h-[32%] w-[26%] -rotate-[14deg] bg-white text-slate-900",
      title: "Creative",
      subtitle: "Inspiration / 9:41",
    },
    {
      className:
        "left-[26%] top-[2%] h-[28%] w-[24%] rotate-[14deg] bg-[#6d28d9] text-white",
      title: "Music",
      subtitle: "Fresh mixes",
    },
    {
      className:
        "left-[52%] top-[4%] h-[36%] w-[28%] -rotate-[16deg] bg-black text-white",
      title: "Bread",
      subtitle: "Sourdough / seeds",
    },
    {
      className:
        "left-[78%] top-[4%] h-[30%] w-[24%] rotate-[10deg] bg-white text-slate-900",
      title: "Charts",
      subtitle: "Square / today",
    },
    {
      className:
        "left-[12%] top-[38%] h-[34%] w-[27%] rotate-[14deg] bg-[#f9d24a] text-slate-900",
      title: "Manage",
      subtitle: "Anxiety / breathing",
    },
    {
      className:
        "left-[38%] top-[37%] h-[32%] w-[25%] -rotate-[16deg] bg-[#f6a04d] text-slate-950",
      title: "Stats",
      subtitle: "Daily focus",
    },
    {
      className:
        "left-[66%] top-[39%] h-[33%] w-[26%] rotate-[12deg] bg-white text-slate-900",
      title: "Cool stuff",
      subtitle: "Discover",
    },
    {
      className:
        "left-[24%] top-[73%] h-[26%] w-[25%] -rotate-[12deg] bg-white text-slate-900",
      title: "Artifact",
      subtitle: "Read on / learn",
    },
    {
      className:
        "left-[53%] top-[73%] h-[27%] w-[23%] rotate-[13deg] bg-[#171717] text-white",
      title: "Fet Seminary",
      subtitle: "Cinema poster",
    },
    {
      className:
        "left-[77%] top-[73%] h-[25%] w-[24%] -rotate-[10deg] bg-white text-slate-900",
      title: "Shop",
      subtitle: "New arrivals",
    },
  ];

  return (
    <div
      className={cn(
        "relative hidden h-full w-full overflow-hidden bg-[#f5f1ea]",
        className,
      )}
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.75),transparent_40%)]" />

      <div className="absolute -left-12 top-0 h-[120%] w-[120%] rotate-[10deg]">
        {tiles.map((tile) => (
          <div
            key={tile.title}
            className={cn(
              "absolute overflow-hidden rounded-[2rem] border border-black/10 shadow-[0_30px_80px_rgba(0,0,0,0.16)]",
              tile.className,
            )}
          >
            <div className="flex h-full w-full flex-col justify-between p-5">
              <div className="flex items-center justify-between text-[11px] font-medium uppercase tracking-[0.24em] opacity-70">
                <span>{tile.title}</span>
                <span>9:41</span>
              </div>

              <div className="space-y-2">
                <div className="h-16 w-full rounded-2xl border border-black/10 bg-white/20 backdrop-blur-sm" />
                <p className="text-sm font-semibold leading-tight">
                  {tile.subtitle}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
