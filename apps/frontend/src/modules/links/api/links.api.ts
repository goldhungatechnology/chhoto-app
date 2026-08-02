import type { Client } from "@/http/rest";
import type {
  CreateLinkRequest,
  CreateLinkResponse,
  ListLinksResponse,
  ListLinkSessionsResponse,
  LinkData,
} from "../types";

import { ENDPOINTS } from "./endpoints";

export class LinksApi {
  private client: Client;

  constructor(client: Client) {
    this.client = client;
  }

  createLink = (payload: CreateLinkRequest): Promise<CreateLinkResponse> => {
    return this.client.post<CreateLinkResponse>(ENDPOINTS.CREATE, payload);
  };

  listLinks = (): Promise<ListLinksResponse> => {
    return this.client.get<ListLinksResponse>(ENDPOINTS.LIST);
  };

  updateLink = (
    linkUuid: string,
    payload: { title: string | null },
  ): Promise<{ data: LinkData; message: string }> => {
    return this.client.patch<{ data: LinkData; message: string }>(
      ENDPOINTS.UPDATE(linkUuid),
      payload,
    );
  };

  listLinkSessions = (
    linkUuid: string,
  ): Promise<ListLinkSessionsResponse> => {
    return this.client.get<ListLinkSessionsResponse>(
      ENDPOINTS.SESSIONS(linkUuid),
    );
  };
}
