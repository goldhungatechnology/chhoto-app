import { AuthGuard } from "@/modules/auth";
import { Navbar } from "@/shared/layout/navbar";
import { SidebarProvider } from "@/shared/components/ui/sidebar";
import { AppSidebar } from "@/shared/layout/sidebar/sidebar";

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <AuthGuard>
        <SidebarProvider>
          <AppSidebar />
          <div className="flex flex-col w-full">
            <Navbar />
            {children}
          </div>
        </SidebarProvider>
      </AuthGuard>
    </>
  );
}
