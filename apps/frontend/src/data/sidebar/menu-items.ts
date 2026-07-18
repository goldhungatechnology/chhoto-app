import { LucideIcon } from "lucide-react";
import {
  Home,
  BarChart3,
  Link2,
} from "lucide-react";

export interface NavItem {
  title: string;
  url: string;
  icon: LucideIcon;
}

export const mainNavItems: NavItem[] = [
  {
    title: "Dashboard",
    url: "/dashboard",
    icon: Home,
  },
  {
    title: "Links",
    url: "/links",
    icon: Link2,
  },
  {
    title: "Analytics",
    url: "/analytics",
    icon: BarChart3,
  },
];
