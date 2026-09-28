from types import SimpleNamespace
from datetime import datetime, timezone

from ecowatt.services.participant_auth import AuthenticatedParticipant
from ecowatt.utils import session as session_utils


class FakeState(dict):
    __getattr__ = dict.__getitem__

    def __setattr__(self, key, value):
        self[key] = value


def test_reset_to_preset_uses_official_preset_loader(monkeypatch):
    state = FakeState()
    monkeypatch.setattr(session_utils, "st", SimpleNamespace(session_state=state))
    monkeypatch.setattr(
        session_utils,
        "load_official_presets",
        lambda: [{"id": "preset-a", "name": "Casa eficiente", "tariff": 0.92}],
    )
    monkeypatch.setattr(session_utils, "convert_preset_to_appliances", lambda preset: [preset["name"]])

    session_utils.reset_to_preset("preset-a")

    assert state.appliances == ["Casa eficiente"]
    assert state.tariff == 0.92
    assert state.active_preset_name == "Casa eficiente"


def test_authenticated_profile_is_restored_into_shared_session_state(monkeypatch):
    state = FakeState()
    monkeypatch.setattr(session_utils, "st", SimpleNamespace(session_state=state))
    participant = AuthenticatedParticipant(
        participant_id="participant-1",
        username="aluno-01",
        session_token="opaque-token",
        expires_at=datetime(2026, 10, 28, tzinfo=timezone.utc),
        full_name="Ana Silva",
        participant_role="Aluno",
        class_group="8A",
        age_group="11–14",
        gender="Mulher",
    )

    session_utils._set_authenticated_participant(participant)

    assert state.profile_complete is True
    assert state.full_name == "Ana Silva"
    assert state.role == "Aluno"
    assert state.class_group == "8A"