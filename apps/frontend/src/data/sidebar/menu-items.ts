import { LucideIcon } from "lucide-react";
import {
  Home,
  BarChart3,
  QrCode,
  HelpCircle,
  Settings,
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
  {
    title: "QR Codes",
    url: "/qr-codes",
    icon: QrCode,
  },
];

export const footerNavItems: NavItem[] = [
  {
    title: "Help Center",
    url: "/help",
    icon: HelpCircle,
  },
  {
    title: "Settings",
    url: "/settings",
    icon: Settings,
  },
];
