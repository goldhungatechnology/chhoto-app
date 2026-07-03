import { CheckCircle2 } from "lucide-react";

// ----------------------------------------------------------------------

export default function VerifySuccess() {
  return (
    <div className="text-center space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="w-16 h-16 mx-auto rounded-full bg-emerald-100 flex items-center justify-center">
        <CheckCircle2 className="w-8 h-8 text-emerald-600" />
      </div>

      <div>
        <h1 className="text-2xl font-semibold text-slate-900">
          Email Verified!
        </h1>

        <p className="mt-2 text-sm text-slate-600">
          Redirecting you to your account...
        </p>
      </div>
    </div>
  );
}
