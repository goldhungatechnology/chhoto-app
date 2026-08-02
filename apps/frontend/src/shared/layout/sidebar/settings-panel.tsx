"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronLeft } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/shared/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/shared/components/ui/sheet";
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/shared/components/ui/sidebar";
import { settingsNavItems } from "@/data/sidebar/settings-menu-items";

const SETTINGS_WIDTH = "15rem";
const SETTINGS_WIDTH_MOBILE = "18rem";
const SETTINGS_ROUTES = ["/profile"];

interface SettingsPanelProps {
  open: boolean;
  onClose: () => void;
}

function SettingsPanelContent({
  onClose,
  closeOnNavigate,
}: {
  onClose: () => void;
  closeOnNavigate: boolean;
}) {
  const pathname = usePathname();

  return (
    <>
      <div className="flex h-14 shrink-0 items-center gap-1 border-b border-sidebar-border/40 px-2">
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={onClose}
          aria-label="Back to main menu"
          className="cursor-pointer"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <span className="text-sm font-semibold">Settings</span>
      </div>

      <div className="flex flex-1 min-h-0 overflow-y-auto p-2">
        <SidebarMenu>
          {settingsNavItems.map((item) => {
            const isActive = pathname === item.url;
            return (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton
                  asChild
                  isActive={isActive}
                  onClick={closeOnNavigate ? onClose : undefined}
                  className="cursor-pointer"
                >
                  <Link href={item.url}>
                    <item.icon className="h-4 w-4" />
                    <span>{item.title}</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            );
          })}
        </SidebarMenu>
      </div>
    </>
  );
}

export function SettingsPanel({ open, onClose }: SettingsPanelProps) {
  const { isMobile, state } = useSidebar();
  const pathname = usePathname();
  const prevPathnameRef = React.useRef(pathname);

  React.useEffect(() => {
    const prevPathname = prevPathnameRef.current;
    prevPathnameRef.current = pathname;

    if (!open) return;

    const isSettingsRoute = (route: string) =>
      SETTINGS_ROUTES.some((r) => route.startsWith(r));

    if (isSettingsRoute(prevPathname) && !isSettingsRoute(pathname)) {
      onClose();
    }
  }, [open, pathname, onClose]);

  if (isMobile) {
    return (
      <Sheet open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
        <SheetContent
          side="left"
          showCloseButton={false}
          className="bg-sidebar p-0 text-sidebar-foreground [&>button]:hidden"
          style={
            {
              width: SETTINGS_WIDTH_MOBILE,
              maxWidth: SETTINGS_WIDTH_MOBILE,
            } as React.CSSProperties
          }
        >
          <SheetHeader className="sr-only">
            <SheetTitle>Settings</SheetTitle>
            <SheetDescription>
              Settings navigation menu.
            </SheetDescription>
          </SheetHeader>
          <SettingsPanelContent onClose={onClose} closeOnNavigate />
        </SheetContent>
      </Sheet>
    );
  }

  const leftOffset =
    state === "collapsed" ? "var(--sidebar-width-icon)" : "var(--sidebar-width)";

  return (
    <>
      <div
        className="relative hidden bg-transparent transition-[width] duration-200 ease-linear md:block"
        style={{ width: open ? SETTINGS_WIDTH : "0px" }}
      />
      <div
        className={cn(
          "fixed inset-y-0 z-50 hidden flex-col bg-sidebar text-sidebar-foreground md:flex",
          open ? "border-r border-sidebar-border/40" : "pointer-events-none",
        )}
        style={
          {
            width: SETTINGS_WIDTH,
            left: leftOffset,
            transform: open
              ? "translateX(0)"
              : `translateX(calc(-1 * (${leftOffset} + ${SETTINGS_WIDTH})))`,
            visibility: open ? "visible" : "hidden",
            transitionProperty: "transform, visibility, border-color",
            transitionDuration: "200ms",
            transitionTimingFunction: "ease-linear",
          } as React.CSSProperties
        }
      >
        <SettingsPanelContent onClose={onClose} closeOnNavigate={false} />
      </div>
    </>
  );
}
