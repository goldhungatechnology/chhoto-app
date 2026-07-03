import { Client } from "@/http/rest";

import { AuthApi } from "./auth.api";

// ----------------------------------------------------------------------

const clientInstance = new Client();

export const authApi = new AuthApi(clientInstance);
