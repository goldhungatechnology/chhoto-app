"use client";

import { ROUTES } from "@/core/config";

import { LoginRegisterLayout, LoginForm } from "../blocks";

export default function LoginSection() {
  const prompt = {
    content: "Don't have an account?",
    title: "Sign up",
    href: ROUTES.AUTH.REGISTER,
  };

  return (
    <LoginRegisterLayout prompt={prompt}>
      <LoginForm />
    </LoginRegisterLayout>
  );
}
