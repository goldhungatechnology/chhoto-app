interface VerificationActionsProps {
  resendCooldown: number;
  //
  onResend: () => void;
}

// ----------------------------------------------------------------------

export default function VerifyActions({
  resendCooldown,
  //
  onResend,
}: VerificationActionsProps) {
  return (
    <div className="flex items-center justify-center gap-1 text-sm text-slate-600 dark:text-gray-300">
      <span>Didn&apos;t receive the code?</span>

      <button
        onClick={onResend}
        disabled={resendCooldown > 0}
        className="cursor-pointer font-medium text-slate-900 hover:text-slate-700 disabled:text-slate-400 dark:text-primary disabled:cursor-not-allowed transition-colors"
      >
        {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : "Resend code"}
      </button>
    </div>
  );
}
