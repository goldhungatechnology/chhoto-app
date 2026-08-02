"use client";

import * as React from "react";
import { usePathname } from "next/navigation";

export function TopLoader() {
  const pathname = usePathname();
  const initialPathnameRef = React.useRef(pathname);
  const [started, setStarted] = React.useState(false);

  React.useEffect(() => {
    if (initialPathnameRef.current !== pathname) {
      setStarted(true);
    }
  }, [pathname]);

  if (!started) return null;

  return (
    <div
      key={pathname}
      aria-hidden="true"
      className="pointer-events-none fixed inset-x-0 top-0 z-[9999] h-[2px] overflow-hidden"
    >
      <div className="h-full w-0 bg-[#6366f1] shadow-[0_0_8px_#6366f1,0_0_20px_#6366f1] [animation:top-loader-fill_500ms_ease-out_forwards,top-loader-fade_300ms_ease-out_500ms_forwards]" />
    </div>
  );
}
