import pytest

from ecowatt.services.quiz_service import (
    PERSISTED_QUIZ_ID,
    Quiz,
    QuizQuestion,
    QuizService,
    SupabaseQuizRepository,
    export_minimized_results,
)


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


def test_attempt_keeps_its_original_question_set_after_quiz_grows():
    original = quiz()
    service = QuizService(seed=1)
    attempt = service.start(original, "session-original")
    attempt.question_ids = ["one"]
    service.answer(original, attempt, "one", 0)

    expanded = Quiz(
        original.id,
        original.title,
        original.questions + [
            QuizQuestion("three", "Outra pergunta?", ("Sim", "Não"), 0, "Explicação nova.")
        ],
    )
    service.finish(expanded, attempt)

    assert attempt.score == 1
    assert [result["question_id"] for result in service.result(expanded, attempt)] == ["one"]


def test_result_export_omits_names_by_default():
    service = QuizService()
    attempt = service.start(quiz(), "session-3")
    exported = export_minimized_results([attempt])
    assert "participant_name" not in exported[0]


class FakeQuizRepository:
    def __init__(self):
        self.enabled = True
        self.attempts = {}
        self.answers = {}

    def quiz_is_enabled(self, quiz_id):
        return self.enabled

    def find_attempt(self, quiz_id, participant_id):
        record = self.attempts.get((quiz_id, participant_id))
        if record:
            record["answers"] = self.answers.get(record["id"], {}).copy()
        return record

    def create_attempt(self, quiz_id, participant_id, session_id, question_ids):
        record = {
            "id": f"attempt-{len(self.attempts) + 1}",
            "quiz_id": quiz_id,
            "participant_id": participant_id,
            "session_id": session_id,
            "question_order": question_ids,
            "score": 0,
            "completed_at": None,
            "participation_code": None,
            "answers": {},
        }
        self.attempts[(quiz_id, participant_id)] = record
        return record

    def save_answer(self, attempt_id, question_id, selected_option, correct):
        self.answers.setdefault(attempt_id, {})[question_id] = selected_option

    def finish_attempt(self, attempt_id, participant_id, score, participation_code):
        record = next(record for record in self.attempts.values() if record["id"] == attempt_id)
        record["score"] = score
        record["completed_at"] = "2026-09-28T00:00:00+00:00"
        record["participation_code"] = participation_code


def test_persistent_quiz_attempt_restores_answers_and_final_score():
    current = quiz()
    repository = FakeQuizRepository()
    first_service = QuizService(seed=1, repository=repository)
    first_attempt = first_service.start(current, "visit-1", "participant-1")
    first_question = first_attempt.question_ids[0]
    first_service.answer(current, first_attempt, first_question, 0)

    next_service = QuizService(seed=2, repository=repository)
    restored = next_service.start(current, "visit-2", "participant-1")
    assert restored.id == first_attempt.id
    assert restored.question_ids == first_attempt.question_ids
    assert restored.answers == {first_question: 0}

    for question in current.questions:
        if question.id not in restored.answers:
            next_service.answer(current, restored, question.id, question.correct_option)
    next_service.finish(current, restored)

    after_completion = QuizService(repository=repository).start(current, "visit-3", "participant-1")
    assert after_completion.score == 2
    assert after_completion.id == first_attempt.id


def test_persistent_quiz_rejects_disabled_quiz():
    current = quiz()
    repository = FakeQuizRepository()
    repository.enabled = False

    with pytest.raises(ValueError, match="desabilitado"):
        QuizService(repository=repository).start(current, "visit-1", "participant-1")


def test_persistent_quiz_attempts_are_isolated_by_participant():
    current = quiz()
    repository = FakeQuizRepository()
    service = QuizService(seed=1, repository=repository)

    first = service.start(current, "visit-1", "participant-1")
    second = service.start(current, "visit-1", "participant-2")

    assert first.id != second.id
    assert first.participant_id != second.participant_id


class FakeQuizContentClient:
    def __init__(self):
        self.calls = []

    def request(self, method, table, *, filters=None, payload=None, prefer=None):
        self.calls.append((method, table, filters))
        if table == "event_quizzes":
            return 200, [{
                "id": PERSISTED_QUIZ_ID,
                "title": "Desafio EcoWatt",
                "enabled": True,
                "reward_enabled": False,
            }]
        if table == "quiz_questions":
            return 200, [
                {
                    "id": "question-1",
                    "prompt": "Qual unidade mede energia?",
                    "explanation": "kWh mede energia consumida.",
                    "options": ["kWh", "Watt", "Volt"],
                    "correct_option": 0,
                },
                {
                    "id": "question-2",
                    "prompt": "Qual unidade mede potência?",
                    "explanation": "Watt mede potência.",
                    "options": ["kWh", "Watt", "Volt"],
                    "correct_option": 1,
                },
            ]
        raise AssertionError(f"Unexpected table: {table}")


def test_load_quiz_uses_all_published_questions_from_supabase():
    client = FakeQuizContentClient()
    quiz = SupabaseQuizRepository(client).load_quiz(PERSISTED_QUIZ_ID)

    assert quiz.id == PERSISTED_QUIZ_ID
    assert quiz.enabled is True
    assert len(quiz.questions) == 2
    assert quiz.questions[1].options == ("kWh", "Watt", "Volt")
    assert quiz.questions[1].correct_option == 1
    question_query = next(call for call in client.calls if call[1] == "quiz_questions")
    assert question_query[2]["status"] == "eq.published"
