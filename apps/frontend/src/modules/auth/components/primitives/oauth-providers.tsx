import { Separator } from "@/shared/components/ui/separator";
import { Button } from "@/shared/components/ui/button";

import { API_BASE_URL } from "@/core/config/api";
import Google from "../../../../../public/assets/icons/google";

// ----------------------------------------------------------------------

export default function OAuthProviders() {
  const handleGoogleLogin = () => {
    window.location.href = `${API_BASE_URL}/auth/oauth/login/google`;
  };

  return (
    <div>
      <Button
        type="button"
        variant="outline"
        className="h-11 w-full rounded-full border-slate-200 bg-white text-slate-900 shadow-none hover:bg-slate-50"
        onClick={handleGoogleLogin}
      >
        <Google />
        Continue with Google
      </Button>

      <div className="relative my-6">
        <Separator className="bg-slate-200" />

        <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white px-3 text-sm text-slate-500">
          or
        </span>
      </div>
    </div>
  );
}
