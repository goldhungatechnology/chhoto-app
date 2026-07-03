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
    <LoginRegisterLayout prompt={prompt} footerContent={
      <div className="text-center">
        <Link
          href={ROUTES.AUTH.LOGIN}
          className="text-sm text-slate-500 underline-offset-4 hover:text-slate-700 hover:underline"
        >
          Already have an account? Sign in
        </Link>
      </div>
    }>
      <RegisterForm />
    </LoginRegisterLayout>
  );
}
