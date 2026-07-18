export type PlatformCategory =
  "web" | "instagram" | "youtube" | "tiktok" | "ads" | "other";

export interface CreateLinkInput {
  title?: string;
  url: string;
  platform: PlatformCategory;
  generateQr: boolean;
  autoExpire: boolean;
  expiryDate?: string;
}

export interface ShortLink {
  id: string;
  title: string;
  originalUrl: string;
  shortUrl: string;
  platform: PlatformCategory;
  qrCodeUrl?: string;
  expiryDate?: string;
  createdAt: string;
}

export interface CreateLinkRequest {
  destination_url: string;
  custom_slug?: string;
  title?: string;
  tags?: string[];
  auto_expire?: string | null;
}

export interface LinkData {
  uuid: string;
  destination_url: string;
  short_url: string;
  title: string | null;
  tags: string[] | null;
  auto_expire: string | null;
  total_clicks: number;
  created_at: string;
  generateQr: boolean;
}

export interface CreateLinkResponse {
  data: LinkData;
  message: string;
}

export interface ListLinksResponse {
  data: LinkData[];
  message: string;
}
