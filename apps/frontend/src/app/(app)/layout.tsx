import { AuthGuard } from "@/modules/auth";
import { SidebarProvider } from "@/shared/components/ui/sidebar";
import { AppShell } from "@/shared/layout/app-shell";

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    // <AuthGuard>
    <SidebarProvider>
      <AppShell>{children}</AppShell>
    </SidebarProvider>
    // </AuthGuard>
  );
}
