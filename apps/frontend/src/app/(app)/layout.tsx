import { AuthGuard } from "@/modules/auth";
import { Navbar } from "@/shared/components/custom/navbar";

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <AuthGuard>
        <Navbar />
        {children}
      </AuthGuard>
    </>
  );
}
