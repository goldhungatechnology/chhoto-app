export default function ResetPasswordHeader() {
  return (
    <header className="flex flex-col gap-1.5">
      <h2 className="text-2xl font-semibold tracking-tight">
        Set new password
      </h2>

      <p className="text-sm text-muted-foreground leading-relaxed">
        Choose a strong password to protect your account.
      </p>
    </header>
  );
}
