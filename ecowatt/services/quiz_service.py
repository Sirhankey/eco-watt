"""Educational quiz domain service with one attempt per session."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from random import Random
from typing import Optional
from uuid import uuid4

from ecowatt.services.supabase_server import SupabaseServerClient, SupabaseServerError


PERSISTED_QUIZ_ID = "11111111-1111-4111-8111-111111111111"
PERSISTED_QUESTION_IDS = (
    "22222222-2222-4222-8222-222222222221",
    "22222222-2222-4222-8222-222222222222",
    "22222222-2222-4222-8222-222222222223",
)


class QuizPersistenceUnavailable(RuntimeError):
    """Raised when quiz attempts cannot be persisted or restored."""


class ExistingQuizAttempt(RuntimeError):
    """Raised when another request already created the participant's attempt."""


class SupabaseQuizRepository:
    """Server-only persistence for attempts and answers."""

    def __init__(self, client: SupabaseServerClient | None = None) -> None:
        self.client = client or SupabaseServerClient()

    def _request(self, method: str, table: str, **kwargs):
        try:
            return self.client.request(method, table, **kwargs)
        except SupabaseServerError as error:
            raise QuizPersistenceUnavailable("Não foi possível acessar as tentativas do quiz.") from error

    def quiz_is_enabled(self, quiz_id: str) -> bool:
        status, rows = self._request(
            "GET", "event_quizzes", filters={"select": "id,enabled", "id": f"eq.{quiz_id}", "limit": "1"}
        )
        if status < 200 or status >= 300:
            raise QuizPersistenceUnavailable("Não foi possível verificar se o quiz está ativo.")
        return bool(rows and rows[0].get("enabled"))

    def find_attempt(self, quiz_id: str, participant_id: str) -> dict | None:
        status, rows = self._request(
            "GET",
            "quiz_attempts",
            filters={
                "select": "id,quiz_id,participant_id,session_id,question_order,score,completed_at,participation_code",
                "quiz_id": f"eq.{quiz_id}",
                "participant_id": f"eq.{participant_id}",
                "limit": "1",
            },
        )
        if status < 200 or status >= 300:
            raise QuizPersistenceUnavailable("Não foi possível carregar sua tentativa do quiz.")
        if not rows:
            return None
        record = rows[0]
        answer_status, answers = self._request(
            "GET",
            "quiz_answers",
            filters={
                "select": "question_id,selected_option",
                "attempt_id": f"eq.{record['id']}",
            },
        )
        if answer_status < 200 or answer_status >= 300:
            raise QuizPersistenceUnavailable("Não foi possível carregar suas respostas do quiz.")
        record["answers"] = {str(answer["question_id"]): int(answer["selected_option"]) for answer in answers or []}
        return record

    def create_attempt(self, quiz_id: str, participant_id: str, session_id: str, question_ids: list[str]) -> dict:
        status, rows = self._request(
            "POST",
            "quiz_attempts",
            payload={
                "quiz_id": quiz_id,
                "participant_id": participant_id,
                "session_id": session_id,
                "question_order": question_ids,
            },
            prefer="return=representation",
        )
        if status == 409:
            raise ExistingQuizAttempt
        if status < 200 or status >= 300 or not rows:
            raise QuizPersistenceUnavailable("Não foi possível iniciar sua tentativa do quiz.")
        rows[0]["answers"] = {}
        return rows[0]

    def save_answer(self, attempt_id: str, question_id: str, selected_option: int, correct: bool) -> None:
        status, _ = self._request(
            "POST",
            "quiz_answers",
            filters={"on_conflict": "attempt_id,question_id"},
            payload={
                "attempt_id": attempt_id,
                "question_id": question_id,
                "selected_option": selected_option,
                "is_correct": correct,
            },
            prefer="resolution=merge-duplicates,return=minimal",
        )
        if status < 200 or status >= 300:
            raise QuizPersistenceUnavailable("Não foi possível salvar sua resposta.")

    def finish_attempt(self, attempt_id: str, participant_id: str, score: int, participation_code: str | None) -> None:
        status, _ = self._request(
            "PATCH",
            "quiz_attempts",
            filters={"id": f"eq.{attempt_id}", "participant_id": f"eq.{participant_id}"},
            payload={
                "score": score,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "participation_code": participation_code,
            },
            prefer="return=minimal",
        )
        if status < 200 or status >= 300:
            raise QuizPersistenceUnavailable("Não foi possível finalizar sua tentativa do quiz.")

@dataclass(frozen=True)
class QuizQuestion:
    id: str
    prompt: str
    options: tuple[str, ...]
    correct_option: int
    explanation: str

    def __post_init__(self) -> None:
        if len(self.options) < 2 or self.correct_option not in range(len(self.options)):
            raise ValueError("Pergunta de quiz invalida.")
        if not self.prompt.strip() or not self.explanation.strip():
            raise ValueError("Pergunta e explicacao sao obrigatorias.")


@dataclass
class Quiz:
    id: str
    title: str
    questions: list[QuizQuestion]
    enabled: bool = True
    reward_enabled: bool = False


@dataclass
class QuizAttempt:
    id: str
    quiz_id: str
    session_id: str
    question_ids: list[str]
    participant_id: Optional[str] = None
    answers: dict[str, int] = field(default_factory=dict)
    score: Optional[int] = None
    participation_code: Optional[str] = None


class QuizService:
    def __init__(self, seed: Optional[int] = None, repository=None) -> None:
        self._random = Random(seed)
        self.repository = repository
        self.attempts: dict[tuple[str, str], QuizAttempt] = {}

    def start(self, quiz: Quiz, session_id: str, participant_id: str | None = None) -> QuizAttempt:
        if not quiz.enabled:
            raise ValueError("Este quiz esta desabilitado.")
        if self.repository is not None:
            if not participant_id:
                raise ValueError("A identidade do participante e obrigatoria para persistir o quiz.")
            if not self.repository.quiz_is_enabled(quiz.id):
                raise ValueError("Este quiz esta desabilitado.")
            existing = self.repository.find_attempt(quiz.id, participant_id)
            if existing is None:
                question_ids = [question.id for question in quiz.questions]
                self._random.shuffle(question_ids)
                try:
                    existing = self.repository.create_attempt(quiz.id, participant_id, session_id, question_ids)
                except ExistingQuizAttempt:
                    existing = self.repository.find_attempt(quiz.id, participant_id)
                    if existing is None:
                        raise QuizPersistenceUnavailable("Não foi possível recuperar sua tentativa existente.")
            return self._attempt_from_record(existing)

        existing = self.attempts.get((quiz.id, session_id))
        if existing is not None:
            return existing
        questions = list(quiz.questions)
        self._random.shuffle(questions)
        attempt = QuizAttempt(str(uuid4()), quiz.id, session_id, [question.id for question in questions])
        self.attempts[(quiz.id, session_id)] = attempt
        return attempt

    def answer(self, quiz: Quiz, attempt: QuizAttempt, question_id: str, selected_option: int) -> bool:
        question = next((item for item in quiz.questions if item.id == question_id), None)
        if question is None or selected_option not in range(len(question.options)):
            raise ValueError("Resposta de quiz invalida.")
        if attempt.score is not None:
            raise ValueError("Esta tentativa ja foi concluida.")
        is_correct = selected_option == question.correct_option
        if self.repository is not None:
            self.repository.save_answer(attempt.id, question_id, selected_option, is_correct)
        attempt.answers[question_id] = selected_option
        return is_correct

    def finish(self, quiz: Quiz, attempt: QuizAttempt) -> QuizAttempt:
        if len(attempt.answers) != len(quiz.questions):
            raise ValueError("Responda todas as perguntas antes de finalizar.")
        score = sum(
            1 for question in quiz.questions if attempt.answers.get(question.id) == question.correct_option
        )
        participation_code = None
        if quiz.reward_enabled:
            participation_code = f"ECO-{uuid4().hex[:8].upper()}"
        if self.repository is not None:
            self.repository.finish_attempt(attempt.id, attempt.participant_id, score, participation_code)
        attempt.score = score
        attempt.participation_code = participation_code
        return attempt

    def result(self, quiz: Quiz, attempt: QuizAttempt) -> list[dict[str, object]]:
        return [
            {
                "question_id": question.id,
                "correct": attempt.answers.get(question.id) == question.correct_option,
                "explanation": question.explanation,
            }
            for question in quiz.questions
        ]

    @staticmethod
    def _attempt_from_record(record: dict) -> QuizAttempt:
        question_ids = record.get("question_order") or []
        if isinstance(question_ids, str):
            import json

            question_ids = json.loads(question_ids)
        completed_at = record.get("completed_at")
        return QuizAttempt(
            id=str(record["id"]),
            quiz_id=str(record["quiz_id"]),
            session_id=str(record["session_id"]),
            question_ids=[str(question_id) for question_id in question_ids],
            participant_id=str(record["participant_id"]),
            answers=record.get("answers", {}),
            score=int(record["score"]) if completed_at else None,
            participation_code=record.get("participation_code"),
        )


def export_minimized_results(attempts: list[QuizAttempt], include_names: bool = False) -> list[dict[str, object]]:
    """Create an administrative export without participant names by default."""
    return [
        {
            "attempt_id": attempt.id,
            "quiz_id": attempt.quiz_id,
            "session_id": attempt.session_id,
            "score": attempt.score,
            "participation_code": attempt.participation_code,
            **({"participant_name": getattr(attempt, "participant_name", None)} if include_names else {}),
        }
        for attempt in attempts
    ]
