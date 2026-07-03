from datetime import UTC, datetime, timedelta

import pytest

from src.modules.workforce.domain.entities.invitation.invitation_entity import (
    InvitationEntity,
    InvitationStatus,
)


def _make_invitation(**overrides) -> InvitationEntity:
    data = {
        "organization_id": 10,
        "email": "user@example.com",
        "role_id": 5,
        "team_id": None,
        "invited_by_id": 42,
        "hashed_token": "abc123hash",
        "status": InvitationStatus.PENDING,
        "expires_at": datetime.now(UTC) + timedelta(days=7),
        "accepted_at": None,
        "created_by_id": 42,
    }
    data.update(overrides)
    return InvitationEntity(**data)


class TestInvitationStatus:
    def test_all_contains_all_statuses(self):
        assert InvitationStatus.ALL == {
            InvitationStatus.PENDING,
            InvitationStatus.ACCEPTED,
            InvitationStatus.EXPIRED,
            InvitationStatus.REVOKED,
        }


class TestInvitationEntity:
    def test_is_pending_returns_true_when_pending(self):
        inv = _make_invitation(status=InvitationStatus.PENDING)
        assert inv.is_pending() is True

    def test_is_pending_returns_false_when_not_pending(self):
        inv = _make_invitation(status=InvitationStatus.ACCEPTED)
        assert inv.is_pending() is False

    def test_is_revoked_returns_true_when_revoked(self):
        inv = _make_invitation(status=InvitationStatus.REVOKED)
        assert inv.is_revoked() is True

    def test_is_revoked_returns_false_when_not_revoked(self):
        inv = _make_invitation(status=InvitationStatus.PENDING)
        assert inv.is_revoked() is False

    def test_is_accepted_returns_true_when_accepted(self):
        inv = _make_invitation(status=InvitationStatus.ACCEPTED)
        assert inv.is_accepted() is True

    def test_is_accepted_returns_false_when_not_accepted(self):
        inv = _make_invitation(status=InvitationStatus.PENDING)
        assert inv.is_accepted() is False

    def test_is_expired_returns_true_when_expiry_in_past(self):
        inv = _make_invitation(expires_at=datetime.now(UTC) - timedelta(hours=1))
        assert inv.is_expired() is True

    def test_is_expired_returns_false_when_expiry_in_future(self):
        inv = _make_invitation(expires_at=datetime.now(UTC) + timedelta(days=1))
        assert inv.is_expired() is False

    def test_is_expired_accepts_custom_now(self):
        now = datetime.now(UTC)
        inv = _make_invitation(expires_at=now - timedelta(hours=1))
        assert inv.is_expired(now=now) is True

    def test_is_expired_edge_case_exactly_at_expiry(self):
        now = datetime.now(UTC)
        inv = _make_invitation(expires_at=now)
        assert inv.is_expired(now=now) is True

    def test_is_acceptable_returns_true_when_pending_and_not_expired(self):
        inv = _make_invitation(
            status=InvitationStatus.PENDING,
            expires_at=datetime.now(UTC) + timedelta(days=1),
        )
        assert inv.is_acceptable() is True

    def test_is_acceptable_returns_false_when_not_pending(self):
        inv = _make_invitation(
            status=InvitationStatus.ACCEPTED,
            expires_at=datetime.now(UTC) + timedelta(days=1),
        )
        assert inv.is_acceptable() is False

    def test_is_acceptable_returns_false_when_expired(self):
        inv = _make_invitation(
            status=InvitationStatus.PENDING,
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        assert inv.is_acceptable() is False

    @pytest.mark.parametrize(
        ("invitation_email", "match_email", "expected"),
        [
            ("user@example.com", "user@example.com", True),
            ("User@Example.COM", "user@example.com", True),
            (" user@example.com ", "user@example.com", True),
            ("other@example.com", "user@example.com", False),
            ("user@example.com", None, False),
        ],
    )
    def test_matches_email(self, invitation_email, match_email, expected):
        inv = _make_invitation(email=invitation_email)
        assert inv.matches_email(match_email) is expected

    def test_mark_accepted_sets_status_and_timestamp(self):
        now = datetime.now(UTC)
        inv = _make_invitation()
        inv.mark_accepted(now=now)
        assert inv.status == InvitationStatus.ACCEPTED
        assert inv.accepted_at == now

    def test_mark_accepted_defaults_now(self):
        inv = _make_invitation()
        inv.mark_accepted()
        assert inv.status == InvitationStatus.ACCEPTED
        assert inv.accepted_at is not None

    def test_mark_revoked_sets_status(self):
        inv = _make_invitation()
        inv.mark_revoked()
        assert inv.status == InvitationStatus.REVOKED

    def test_mark_expired_sets_status(self):
        inv = _make_invitation()
        inv.mark_expired()
        assert inv.status == InvitationStatus.EXPIRED
