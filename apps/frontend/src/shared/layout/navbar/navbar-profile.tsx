"use client";

import {
  ChevronDown,
  User,
  LogOut,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/shared/components/ui/dropdown-menu";
import { UserDetails } from "@/modules/auth/api/auth.types";
import { Avatar, AvatarImage, AvatarFallback } from "@/shared/components/ui/avatar";
import { useLogout } from "@/modules/auth/api/hooks";

import Link from "next/link";

interface NavbarProfileProps {
  user: UserDetails;
}

export function NavbarProfile({ user }: NavbarProfileProps) {
  const { logoutAsync } = useLogout();

  const handleLogout = async () => {
    try {
      await logoutAsync();
    } catch {
      // Handled by the hook
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="flex gap-4 items-center hover:cursor-pointer">
          <Avatar>
            <AvatarImage src={user?.avatar || ""} />
            <AvatarFallback
              className="text-white font-bold"
              style={{ backgroundColor: user?.avatar_bg || "var(--primary)" }}
            >
              {user?.full_name?.split("")[0]}
            </AvatarFallback>
          </Avatar>

          <div className="hidden sm:flex flex-col justify-center">
            <span className="text-xs font-bold text-foreground leading-snug">
              {user.full_name}
            </span>
          </div>
          <ChevronDown className="w-4 h-4 text-muted-foreground/60 shrink-0 hidden sm:block transition-transform duration-200 group-data-open:rotate-180" />
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-56 p-2 rounded-2xl">
        <DropdownMenuLabel className="font-normal px-2.5 py-2">
          <div className="flex flex-col space-y-1">
            <p className="text-xs font-bold leading-none text-foreground">
              {user.full_name}
            </p>
            <p className="text-[10px] leading-none text-muted-foreground">
              {user.email}
            </p>
          </div>
        </DropdownMenuLabel>

        <DropdownMenuSeparator className="-mx-2 my-1" />

        <DropdownMenuItem className="cursor-pointer rounded-xl" asChild>
          <Link href="/profile" className="flex items-center w-full">
            <User className="mr-2.5 h-4 w-4 text-muted-foreground/85" />
            <span>My Profile</span>
          </Link>
        </DropdownMenuItem>

        <DropdownMenuSeparator className="-mx-2 my-1" />

        <DropdownMenuItem onClick={handleLogout} className="cursor-pointer rounded-xl text-destructive focus:bg-destructive/10 focus:text-destructive dark:focus:bg-destructive/20">
          <LogOut className="mr-2.5 h-4 w-4" />
          <span>Log out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
