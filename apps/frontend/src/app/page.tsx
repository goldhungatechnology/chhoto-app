import { ROUTES } from "@/core/config";
import { redirect } from "next/navigation";

// ----------------------------------------------------------------------

export default function Home() {
  redirect(ROUTES.DASHBOARD.ROOT);
}
