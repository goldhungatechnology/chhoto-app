"use client";

import {
  ChevronDown,
  User,
  Settings,
  CreditCard,
  LogOut,
  HelpCircle,
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

interface NavbarProfileProps {
  user: UserDetails;
}

export function NavbarProfile({ user }: NavbarProfileProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="flex gap-4 items-center hover:cursor-pointer">
          <Avatar>
            <AvatarImage src={user?.avatar || ""} />
            <AvatarFallback className="bg-primary text-background">
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

        <DropdownMenuItem className="cursor-pointer rounded-xl">
          <User className="mr-2.5 h-4 w-4 text-muted-foreground/85" />
          <span>My Profile</span>
        </DropdownMenuItem>

        <DropdownMenuItem className="cursor-pointer rounded-xl">
          <Settings className="mr-2.5 h-4 w-4 text-muted-foreground/85" />
          <span>Settings</span>
        </DropdownMenuItem>

        <DropdownMenuItem className="cursor-pointer rounded-xl">
          <CreditCard className="mr-2.5 h-4 w-4 text-muted-foreground/85" />
          <span>Billing & Plans</span>
        </DropdownMenuItem>

        <DropdownMenuSeparator className="-mx-2 my-1" />

        <DropdownMenuItem className="cursor-pointer rounded-xl">
          <HelpCircle className="mr-2.5 h-4 w-4 text-muted-foreground/85" />
          <span>Help & Support</span>
        </DropdownMenuItem>

        <DropdownMenuSeparator className="-mx-2 my-1" />

        <DropdownMenuItem className="cursor-pointer rounded-xl text-destructive focus:bg-destructive/10 focus:text-destructive dark:focus:bg-destructive/20">
          <LogOut className="mr-2.5 h-4 w-4" />
          <span>Log out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
