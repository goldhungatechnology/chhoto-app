import { LucideIcon } from "lucide-react";
import { UserRound } from "lucide-react";

export interface SettingsNavItem {
  title: string;
  url: string;
  icon: LucideIcon;
}

export const settingsNavItems: SettingsNavItem[] = [
  {
    title: "Personal Information",
    url: "/profile",
    icon: UserRound,
  },
];
