import { Client } from "@/http/rest";
import { LinksApi } from "./links.api";

const clientInstance = new Client();

export const linksApi = new LinksApi(clientInstance);
