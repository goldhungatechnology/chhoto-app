import { Mail } from "lucide-react";

// ----------------------------------------------------------------------

interface VerifyHeaderProps {
  email: string;
}

// ----------------------------------------------------------------------

export default function VerifyHeader({ email }: VerifyHeaderProps) {
  return (
    <>
      <div className="w-14 h-14 mx-auto rounded-2xl bg-slate-100 flex items-center justify-center">
        <Mail className="size-7 text-slate-700" />
      </div>

      <div className="text-center space-y-2">
        <h1 className="text-2xl sm:text-3xl font-semibold text-slate-900">
          Verify your email
        </h1>

        <p className="text-sm sm:text-base text-slate-600 leading-relaxed">
          We sent a 6-digit code to{" "}
          <span className="font-medium text-slate-900">{email}</span>
          <br />
          Enter it below to continue.
        </p>
      </div>
    </>
  );
}
