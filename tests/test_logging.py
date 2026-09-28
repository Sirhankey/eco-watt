from ecowatt.utils import logging as event_logging


def test_track_event_separates_participant_and_visit_ids(monkeypatch):
    captured = {}

    class FakeState(dict):
        __getattr__ = dict.__getitem__

        def __setattr__(self, key, value):
            self[key] = value

    class FakeStreamlit:
        session_state = FakeState({
            "participant_id": "participant-uuid",
            "username": "student-01",
            "analytics_session_id": "visit-uuid",
        })

    class FakeLogger:
        def info(self, message):
            captured["message"] = message

    monkeypatch.setattr(event_logging, "st", FakeStreamlit())
    monkeypatch.setattr(event_logging, "_get_logger", lambda: FakeLogger())
    monkeypatch.setattr(event_logging, "save_event", lambda event: captured.setdefault("event", event))

    event_logging.track_event("page_view", page="quiz")

    event = captured["event"]
    assert event["participant_id"] == "participant-uuid"
    assert event["session_id"] == "visit-uuid"
    assert "participant_name" not in event
    assert "class_group" not in event