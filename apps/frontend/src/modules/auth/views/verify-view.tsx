"use client";

import { VerifyForm } from "@/modules/auth/components";
import { useMe } from "../api/hooks";
import { redirect } from "next/navigation";
import { ROUTES } from "@/core/config";

export default function VerifyView() {
  const { data } = useMe();
  const user = data?.data?.user;
  if (user && user.is_email_verified) {
    redirect(ROUTES.DASHBOARD.ROOT);
  }

  return <VerifyForm />;
}
