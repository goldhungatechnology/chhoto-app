import { AlertCircle } from "lucide-react";

import { Alert, AlertDescription } from "@/shared/components/ui/alert";

// ----------------------------------------------------------------------

interface ErrorAlertProps {
  message: string;
}

// ----------------------------------------------------------------------

export function ErrorAlert({ message }: ErrorAlertProps) {
  return (
    <Alert
      variant="destructive"
      className="animate-in fade-in slide-in-from-top-2 duration-300"
    >
      <AlertCircle className="h-4 w-4" />

      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
}
