// ----------------------------------------------------------------------

interface ForgotPasswordHeaderProps {
  isSent?: boolean;
}

// ----------------------------------------------------------------------

export default function ForgotPasswordHeader({
  isSent = false,
}: ForgotPasswordHeaderProps) {
  if (isSent) {
    return (
      <header className="flex flex-col gap-1.5">
        <h2 className="text-2xl font-semibold tracking-tight">
          Check your inbox
        </h2>

        <p className="text-sm text-muted-foreground leading-relaxed">
          If an account is associated with that address, you'll receive a reset
          link within a few minutes.
        </p>
      </header>
    );
  }

  return (
    <header className="flex flex-col gap-1.5">
      <h2 className="text-2xl font-semibold">Forgot password?</h2>

      <p className="text-sm text-muted-foreground leading-relaxed">
        Enter your email and we'll send you a secure link to reset your
        password.
      </p>
    </header>
  );
}
