from types import SimpleNamespace

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