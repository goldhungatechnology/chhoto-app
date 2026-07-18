import type { Client } from "@/http/rest";
import type {
  CreateLinkRequest,
  CreateLinkResponse,
  ListLinksResponse,
  ListLinkSessionsResponse,
  LinkData,
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

  updateLink = (
    linkUuid: string,
    payload: { title: string | null },
  ): Promise<{ data: LinkData; message: string }> => {
    return this.client.patch<{ data: LinkData; message: string }>(
      `/links/${linkUuid}`,
      payload,
    );
  };

  listLinkSessions = (
    linkUuid: string,
  ): Promise<ListLinkSessionsResponse> => {
    return this.client.get<ListLinkSessionsResponse>(
      `/links/sessions/${linkUuid}`,
    );
  };
}
