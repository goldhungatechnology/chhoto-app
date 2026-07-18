import type { Client } from "@/http/rest";
import type {
  CreateLinkRequest,
  CreateLinkResponse,
  ListLinksResponse,
} from "../types";

export class LinksApi {
  private client: Client;

  constructor(client: Client) {
    this.client = client;
  }

  createLink = (payload: CreateLinkRequest): Promise<CreateLinkResponse> => {
    return this.client.post<CreateLinkResponse>("/links/", payload);
  };

  listLinks = (): Promise<ListLinksResponse> => {
    return this.client.get<ListLinksResponse>("/links/");
  };
}
