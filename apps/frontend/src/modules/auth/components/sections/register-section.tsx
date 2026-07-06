"use client";

import Link from "next/link";

import { ROUTES } from "@/core/config";

import { LoginRegisterLayout, RegisterForm } from "../blocks";

export default function RegisterSection() {
  const prompt = {
    content: "Already have an account?",
    title: "Sign in",
    href: ROUTES.AUTH.LOGIN,
  };

  return (
    <LoginRegisterLayout
      prompt={prompt}
      footerContent={
        <p className="text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link
            href={ROUTES.AUTH.LOGIN}
            className="font-medium text-primary underline-offset-4 hover:underline"
          >
            Login
          </Link>
        </p>
      }
    >
      <RegisterForm />
    </LoginRegisterLayout>
  );
}
