"""Educational quiz domain service with one attempt per session."""
from dataclasses import dataclass, field
from random import Random
from typing import Optional
from uuid import uuid4


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
    answers: dict[str, int] = field(default_factory=dict)
    score: Optional[int] = None
    participation_code: Optional[str] = None


class QuizService:
    def __init__(self, seed: Optional[int] = None) -> None:
        self._random = Random(seed)
        self.attempts: dict[tuple[str, str], QuizAttempt] = {}

    def start(self, quiz: Quiz, session_id: str) -> QuizAttempt:
        if not quiz.enabled:
            raise ValueError("Este quiz esta desabilitado.")
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
        attempt.answers[question_id] = selected_option
        return selected_option == question.correct_option

    def finish(self, quiz: Quiz, attempt: QuizAttempt) -> QuizAttempt:
        if len(attempt.answers) != len(quiz.questions):
            raise ValueError("Responda todas as perguntas antes de finalizar.")
        attempt.score = sum(
            1 for question in quiz.questions if attempt.answers.get(question.id) == question.correct_option
        )
        if quiz.reward_enabled:
            attempt.participation_code = f"ECO-{uuid4().hex[:8].upper()}"
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
