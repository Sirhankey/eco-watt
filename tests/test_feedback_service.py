import pytest

from ecowatt.services.feedback_service import (
    ExperienceFeedbackRepository,
    FeedbackStorageUnavailable,
    build_feedback,
)


class FakeClient:
    def __init__(self, status=201, rows=None):
        self.status = status
        self.rows = rows or []
        self.calls = []

    def request(self, method, table, **kwargs):
        self.calls.append((method, table, kwargs))
        return self.status, self.rows


def test_build_feedback_trims_and_limits_the_optional_text():
    feedback = build_feedback(5, "Sim", "Mais ou menos", "Quiz", "  " + "a" * 400 + "  ")

    assert feedback["rating"] == 5
    assert len(feedback["learned"]) == 300
    assert build_feedback(3, "Não", "Não", "Calculadora", "   ")["learned"] is None


@pytest.mark.parametrize(
    "args",
    [(0, "Sim", "Sim", "Quiz", ""), (6, "Sim", "Sim", "Quiz", ""), (3, "Talvez", "Sim", "Quiz", ""), (3, "Sim", "Sim", "Outro", "")],
)
def test_build_feedback_rejects_invalid_answers(args):
    with pytest.raises(ValueError):
        build_feedback(*args)


def test_save_feedback_ignores_a_second_submission_for_the_same_participant():
    client = FakeClient()
    repository = ExperienceFeedbackRepository(client)

    repository.save_feedback("participant-1", build_feedback(4, "Sim", "Sim", "Quiz", None))

    method, table, kwargs = client.calls[0]
    assert (method, table) == ("POST", "experience_feedback")
    assert kwargs["filters"] == {"on_conflict": "participant_id"}
    assert "ignore-duplicates" in kwargs["prefer"]
    assert kwargs["payload"]["participant_id"] == "participant-1"


def test_has_feedback_reflects_existing_rows_and_storage_errors():
    assert ExperienceFeedbackRepository(FakeClient(200, [{"id": "x"}])).has_feedback("p1")
    assert not ExperienceFeedbackRepository(FakeClient(200, [])).has_feedback("p1")
    with pytest.raises(FeedbackStorageUnavailable):
        ExperienceFeedbackRepository(FakeClient(500)).has_feedback("p1")
