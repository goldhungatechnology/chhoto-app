import { Mail } from "lucide-react";

// ----------------------------------------------------------------------

interface VerifyHeaderProps {
  email: string;
}

// ----------------------------------------------------------------------

export default function VerifyHeader({ email }: VerifyHeaderProps) {
  return (
    <>
      <div className="w-14 h-14 mx-auto rounded-2xl dark:bg-primary bg-primary flex items-center justify-center">
        <Mail className="size-7 text-white dark:text-white" />
      </div>

      <div className="text-center space-y-2">
        <h1 className="text-2xl sm:text-3xl font-semibold">
          Verify your email
        </h1>

        <p className="text-sm sm:text-base text-slate-600 dark:text-gray-300 leading-relaxed">
          We sent a 6-digit code to{" "}
          <span className="font-medium text-slate-900 dark:text-primary">
            {email}
          </span>
          <br />
          Enter it below to continue.
        </p>
      </div>
    </>
  );
}
