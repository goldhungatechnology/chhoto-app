import type { Metadata } from "next";
import { Geist, Geist_Mono, Inter } from "next/font/google";

import { APP_NAME } from "@/core/config";

import { cn } from "@/lib/utils";

import { ServerStateProvider } from "@/core/server-state";
import { Snackbar } from "@/shared/components/custom/snackbar";
import { ThemeProvider } from "@/shared/components/custom/theme-provider";
import { ThemeSync } from "@/shared/components/custom/theme-sync";
import { BetaNotice } from "@/shared/components/custom/beta-notice";

import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: APP_NAME,
  description: `${APP_NAME} - Your App`,
  icons: {
    icon: "/favicon.png",
    shortcut: "/favicon.png",
  },
};

// ----------------------------------------------------------------------

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={cn(
        "h-full",
        "antialiased",
        geistSans.variable,
        geistMono.variable,
        "font-sans",
        inter.variable,
      )}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col">
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem={false}
          disableTransitionOnChange
        >
          <ServerStateProvider>
            <ThemeSync />
            {children}
          </ServerStateProvider>
          <Snackbar />
          <BetaNotice />
        </ThemeProvider>
      </body>
    </html>
  );
}
