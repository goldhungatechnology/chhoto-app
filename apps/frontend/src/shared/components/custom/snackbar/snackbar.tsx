"use client";

import { Toaster } from "sonner";

// ----------------------------------------------------------------------

export default function Snackbar() {
  return (
    <Toaster position="top-right" richColors expand className="snackbar" />
  );
}
