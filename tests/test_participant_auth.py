from datetime import datetime, timedelta, timezone

import pytest

from ecowatt.services.participant_auth import (
    AuthenticatedParticipant,
    LoginAttemptLimiter,
    LoginRateLimited,
    ParticipantAuthService,
    UsernameAlreadyTaken,
    hash_session_token,
    normalize_username,
    verify_password,
)


class FakeParticipantRepository:
    def __init__(self):
        self.participants = {}
        self.sessions = {}

    def find_participant(self, username_normalized):
        return self.participants.get(username_normalized)

    def create_participant(self, values):
        username_normalized = values["username_normalized"]
        if username_normalized in self.participants:
            raise UsernameAlreadyTaken
        participant = {"id": f"id-{len(self.participants) + 1}", **values}
        self.participants[username_normalized] = participant
        return participant

    def create_session(self, participant_id, token_hash, expires_at):
        self.sessions[token_hash] = {
            "participant_id": participant_id,
            "expires_at": expires_at.isoformat(),
            "revoked_at": None,
        }

    def find_session(self, token_hash, now):
        session = self.sessions.get(token_hash)
        if not session or session["revoked_at"] or datetime.fromisoformat(session["expires_at"]) <= now:
            return None
        return session

    def revoke_session(self, token_hash, revoked_at):
        if token_hash in self.sessions:
            self.sessions[token_hash]["revoked_at"] = revoked_at.isoformat()

    def get_participant(self, participant_id):
        return next((p for p in self.participants.values() if p["id"] == participant_id), None)

    def update_password(self, participant_id, password_hash):
        participant = self.get_participant(participant_id)
        participant["password_hash"] = password_hash
        participant["must_change_password"] = False

    def update_profile(self, participant_id, profile):
        participant = self.get_participant(participant_id)
        participant.update(profile)


def test_username_normalization_and_validation():
    assert normalize_username("  Ana.Silva_7 ") == "ana.silva_7"
    with pytest.raises(ValueError):
        normalize_username("ána")
    with pytest.raises(ValueError):
        normalize_username("ab")


def test_registration_hashes_password_and_login_is_case_insensitive():
    repository = FakeParticipantRepository()
    service = ParticipantAuthService(repository)

    registered = service.register("Eco.Aluno", "energia-segura")
    stored = repository.participants["eco.aluno"]

    assert isinstance(registered, AuthenticatedParticipant)
    assert registered.participant_id == stored["id"]
    assert stored["password_hash"] != "energia-segura"
    assert verify_password(stored["password_hash"], "energia-segura")
    assert hash_session_token(registered.session_token) in repository.sessions
    assert registered.session_token not in repository.sessions

    logged_in = service.login("ECO.ALUNO", "energia-segura")
    assert logged_in is not None
    assert logged_in.participant_id == registered.participant_id


def test_duplicate_username_and_invalid_password_are_rejected():
    service = ParticipantAuthService(FakeParticipantRepository())
    service.register("aluno-01", "senha-segura")

    with pytest.raises(UsernameAlreadyTaken):
        service.register("ALUNO-01", "outra-senha")
    with pytest.raises(ValueError, match="6 e 128"):
        service.register("aluno-02", "curta")


def test_six_character_password_is_accepted():
    service = ParticipantAuthService(FakeParticipantRepository())

    participant = service.register("aluno-04", "abc123")

    assert service.login("aluno-04", "abc123") is not None


def test_profile_is_required_and_persisted_for_later_logins():
    repository = FakeParticipantRepository()
    service = ParticipantAuthService(repository)
    account = service.register("perfil-01", "senha-segura")

    assert not account.profile_complete
    with pytest.raises(ValueError, match="turma"):
        service.complete_profile(
            account.participant_id,
            "Ana Silva",
            "Aluno",
            " ",
            "11–14",
            "Prefiro não responder",
        )

    service.complete_profile(
        account.participant_id,
        " Ana Silva ",
        "Aluno",
        " 8A ",
        "11–14",
        "Mulher",
    )
    logged_in = service.login("perfil-01", "senha-segura")

    assert logged_in is not None
    assert logged_in.profile_complete
    assert logged_in.full_name == "Ana Silva"
    assert logged_in.class_group == "8A"


def test_non_student_profile_does_not_require_or_store_class_group():
    repository = FakeParticipantRepository()
    service = ParticipantAuthService(repository)
    account = service.register("perfil-02", "senha-segura")

    service.complete_profile(
        account.participant_id,
        "Carlos Silva",
        "Professor",
        "Turma que deve ser descartada",
        "40+",
        "Homem",
    )

    saved = repository.get_participant(account.participant_id)
    assert saved["class_group"] is None


def test_malformed_username_cannot_authenticate_a_valid_reserved_name():
    service = ParticipantAuthService(FakeParticipantRepository())
    service.register("invalid", "senha-segura")

    assert service.login("invalid!", "senha-segura") is None


def test_restore_logout_and_password_change():
    now = datetime(2026, 9, 28, tzinfo=timezone.utc)
    repository = FakeParticipantRepository()
    service = ParticipantAuthService(repository, clock=lambda: now)
    participant = service.register("aluno-02", "senha-temporaria")
    row = repository.participants["aluno-02"]
    row["must_change_password"] = True

    restored = service.restore(participant.session_token)
    assert restored is not None and restored.must_change_password
    assert restored.expires_at == now + timedelta(days=30)

    service.change_password(participant.participant_id, "senha-definitiva")
    assert service.login("aluno-02", "senha-temporaria") is None
    assert service.login("aluno-02", "senha-definitiva") is not None

    service.logout(participant.session_token)
    assert service.restore(participant.session_token) is None


def test_login_failure_limit_blocks_attempts_temporarily():
    current = [0.0]
    limiter = LoginAttemptLimiter(clock=lambda: current[0])
    service = ParticipantAuthService(
        FakeParticipantRepository(),
        limiter=limiter,
    )
    service.register("aluno-03", "senha-segura")

    for _ in range(5):
        assert service.login("aluno-03", "incorreta") is None
    with pytest.raises(LoginRateLimited):
        service.login("aluno-03", "senha-segura")

    current[0] += 61
    assert service.login("aluno-03", "senha-segura") is not None