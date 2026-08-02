export const ENDPOINTS = {
  LIST: "/links/",
  CREATE: "/links/",
  UPDATE: (linkUuid: string) => `/links/${linkUuid}`,
  SESSIONS: (linkUuid: string) => `/links/sessions/${linkUuid}`,
} as const;
