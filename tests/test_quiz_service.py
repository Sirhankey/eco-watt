import pytest

from ecowatt.services.quiz_service import Quiz, QuizQuestion, QuizService, export_minimized_results


def quiz(reward=False):
    return Quiz("q1", "Energia", [
        QuizQuestion("one", "Quanto e 1 kWh?", ("Energia", "Potencia"), 0, "kWh mede energia."),
        QuizQuestion("two", "Qual unidade mede potencia?", ("W", "kWh"), 0, "W mede potencia."),
    ], reward_enabled=reward)


def test_quiz_has_one_attempt_and_generates_symbolic_code():
    service = QuizService(seed=1)
    current = quiz(True)
    attempt = service.start(current, "session-1")
    assert service.start(current, "session-1") is attempt
    for question in current.questions:
        service.answer(current, attempt, question.id, question.correct_option)
    service.finish(current, attempt)
    assert attempt.score == 2
    assert attempt.participation_code.startswith("ECO-")
    with pytest.raises(ValueError, match="concluida"):
        service.answer(current, attempt, current.questions[0].id, 0)


def test_invalid_question_and_incomplete_finish_are_rejected():
    with pytest.raises(ValueError):
        QuizQuestion("bad", "", ("a", "b"), 0, "explanation")
    service = QuizService()
    current = quiz()
    attempt = service.start(current, "session-2")
    with pytest.raises(ValueError, match="todas"):
        service.finish(current, attempt)


def test_result_export_omits_names_by_default():
    service = QuizService()
    attempt = service.start(quiz(), "session-3")
    exported = export_minimized_results([attempt])
    assert "participant_name" not in exported[0]
