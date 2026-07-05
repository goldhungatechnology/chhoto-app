import type { Metadata } from "next";
import { Geist, Geist_Mono, Inter } from "next/font/google";

import { APP_NAME } from "@/core/config";

import { cn } from "@/lib/utils";

import { ServerStateProvider } from "@/core/server-state";
import { Snackbar } from "@/shared/components/custom/snackbar";

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
    >
      <body className="min-h-full flex flex-col">
        <ServerStateProvider>{children}</ServerStateProvider>
        <Snackbar />
      </body>
    </html>
  );
}
