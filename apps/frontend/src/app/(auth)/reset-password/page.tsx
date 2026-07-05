import { Suspense } from "react";
import { ResetPasswordView } from "@/modules/auth/views";

// ----------------------------------------------------------------------

export const metadata = {
  title: "Reset Password",
};

// ----------------------------------------------------------------------

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ResetPasswordView />
    </Suspense>
  );
}
