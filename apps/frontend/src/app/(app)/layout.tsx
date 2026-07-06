import { AuthGuard } from "@/modules/auth";

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <AuthGuard>{children}</AuthGuard>
    </>
  );
}
