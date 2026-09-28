from ecowatt.services.participant_auth import verify_password
from scripts.manage_participant_accounts import (
    cleanup_participants,
    reset_participant_password,
)


class FakeSupabaseClient:
    def __init__(self):
        self.calls = []
        self.tables = {
            "participants": [{"id": "participant-1", "username_normalized": "aluno01"}],
            "participant_sessions": [{"id": "session-1"}],
            "personal_appliances": [{"id": "appliance-1"}],
            "personal_presets": [],
            "catalog_submissions": [],
            "quiz_attempts": [{"id": "attempt-1"}],
        }

    def request(self, method, table, *, filters=None, payload=None, prefer=None):
        self.calls.append((method, table, filters, payload, prefer))
        if method == "GET":
            return 200, self.tables.get(table, [])
        return 204, None


def test_admin_password_reset_stores_only_hash_and_revokes_sessions():
    client = FakeSupabaseClient()

    assert reset_participant_password(client, "Aluno01", "senha-temporaria")

    update = next(call for call in client.calls if call[0] == "PATCH" and call[1] == "participants")
    assert update[3]["must_change_password"] is True
    assert verify_password(update[3]["password_hash"], "senha-temporaria")
    assert "senha-temporaria" not in str(update)
    assert any(call[0] == "PATCH" and call[1] == "participant_sessions" for call in client.calls)


def test_cleanup_defaults_to_preview_and_preserves_pseudonymous_results():
    client = FakeSupabaseClient()

    counts = cleanup_participants(client)

    assert counts["participants"] == 1
    assert counts["quiz_attempts_retained"] == 1
    assert not any(call[0] == "DELETE" for call in client.calls)


def test_cleanup_can_separately_purge_pseudonymous_results():
    client = FakeSupabaseClient()

    cleanup_participants(client, execute=True, purge_results=True)

    deleted_tables = [call[1] for call in client.calls if call[0] == "DELETE"]
    assert deleted_tables == ["participants", "quiz_attempts"]