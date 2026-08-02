"use client";

import { useSessions } from "../api/hooks/use-sessions";
import { useRevokeSession } from "../api/hooks/use-revoke-session";
import { useRevokeAllSessions } from "../api/hooks/use-revoke-all-sessions";

export function useSessionsList() {
  const { data: sessionsData, isLoading: isLoadingSessions } = useSessions();
  const { revokeSessionAsync, isRevokingSession } = useRevokeSession();
  const { revokeAllSessionsAsync, isRevokingAllSessions } = useRevokeAllSessions();

  const sessions = sessionsData?.data || [];

  const handleRevokeSession = async (sessionUuid: string) => {
    try {
      await revokeSessionAsync({ session_uuid: sessionUuid });
    } catch {
      // Handled by toast
    }
  };

  const handleRevokeAllSessions = async () => {
    try {
      await revokeAllSessionsAsync({ keep_current_session: true });
    } catch {
      // Handled by toast
    }
  };

  return {
    sessions,
    isLoadingSessions,
    isRevokingSession,
    isRevokingAllSessions,
    handleRevokeSession,
    handleRevokeAllSessions,
  };
}
