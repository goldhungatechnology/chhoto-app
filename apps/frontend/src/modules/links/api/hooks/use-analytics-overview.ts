import { useQuery } from "@tanstack/react-query";
import { linksApi } from "../index";
import { LinkData, LinkSession } from "../../types";

export interface TimePoint {
  date: string;
  label: string;
  clicks: number;
}

export interface SliceDatum {
  name: string;
  value: number;
}

export interface AnalyticsOverview {
  totalSessions: number;
  clicksPerDay: TimePoint[];
  devices: SliceDatum[];
  browsers: SliceDatum[];
  countries: SliceDatum[];
}

const unknownLabel = (value: string | null, fallback: string) =>
  value?.trim() ? value : fallback;

const normalizeDevice = (device: string | null) => {
  const value = unknownLabel(device, "unknown");
  const lower = value.toLowerCase();
  if (lower === "unknown" || lower === "desktop") return "Desktop";
  return value.charAt(0).toUpperCase() + value.slice(1);
};

const aggregateSessions = (sessions: LinkSession[]): AnalyticsOverview => {
  const dayMap = new Map<string, number>();
  const deviceMap = new Map<string, number>();
  const browserMap = new Map<string, number>();
  const countryMap = new Map<string, number>();

  for (const session of sessions) {
    const date = new Date(session.created_at);
    const dayKey = date.toISOString().slice(0, 10);
    dayMap.set(dayKey, (dayMap.get(dayKey) || 0) + 1);

    const device = normalizeDevice(session.device);
    deviceMap.set(device, (deviceMap.get(device) || 0) + 1);

    const browser = unknownLabel(session.browser, "Unknown");
    browserMap.set(browser, (browserMap.get(browser) || 0) + 1);

    const country = unknownLabel(session.country, "Unknown");
    countryMap.set(country, (countryMap.get(country) || 0) + 1);
  }

  const clicksPerDay = [...dayMap.entries()]
    .map(([key, clicks]) => {
      const label = new Date(`${key}T00:00:00`).toLocaleDateString(undefined, {
        day: "numeric",
        month: "short",
      });
      return { date: key, label, clicks };
    })
    .sort((a, b) => a.date.localeCompare(b.date));

  const toSlice = (map: Map<string, number>) =>
    [...map.entries()]
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);

  return {
    totalSessions: sessions.length,
    clicksPerDay,
    devices: toSlice(deviceMap),
    browsers: toSlice(browserMap),
    countries: toSlice(countryMap),
  };
};

export const useAnalyticsOverview = (links: LinkData[]) => {
  const linkUuids = links.map((link) => link.uuid);

  const query = useQuery({
    queryKey: ["analytics-overview", linkUuids],
    queryFn: async () => {
      const responses = await Promise.all(
        links.map((link) => linksApi.listLinkSessions(link.uuid)),
      );
      return aggregateSessions(responses.flatMap((response) => response.data));
    },
    enabled: linkUuids.length > 0,
  });

  return {
    overview: query.data,
    isLoadingOverview: query.isLoading,
    overviewError: query.error,
    refetchOverview: query.refetch,
  };
};
