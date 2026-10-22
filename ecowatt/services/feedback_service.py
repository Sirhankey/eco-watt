"""One end-of-visit survey per participant, stored server-side."""
from typing import Any

from ecowatt.services.supabase_server import SupabaseServerClient, SupabaseServerError

KNEW_KWH_OPTIONS = ("Sim", "Não", "Não tenho certeza")
HELPED_BILL_OPTIONS = ("Sim", "Mais ou menos", "Não", "Não se aplica")
MAIN_INTEREST_OPTIONS = (
    "Calculadora", "Minha Casa", "PC Builder", "Comparador", "Você Sabia?", "Eficiência", "Modo Apresentação", "Quiz",
)
LEARNED_MAX_LENGTH = 300


class FeedbackStorageUnavailable(RuntimeError):
    """Raised when the feedback table cannot be reached."""


def build_feedback(rating: int, knew_kwh: str, helped_bill: str, main_interest: str, learned: str | None) -> dict[str, Any]:
    if rating not in range(1, 6):
        raise ValueError("Escolha uma nota de 1 a 5.")
    if knew_kwh not in KNEW_KWH_OPTIONS or helped_bill not in HELPED_BILL_OPTIONS or main_interest not in MAIN_INTEREST_OPTIONS:
        raise ValueError("Resposta de avaliação inválida.")
    clean_learned = (learned or "").strip()[:LEARNED_MAX_LENGTH]
    return {
        "rating": rating,
        "knew_kwh": knew_kwh,
        "helped_bill": helped_bill,
        "main_interest": main_interest,
        "learned": clean_learned or None,
    }


class ExperienceFeedbackRepository:
    def __init__(self, client: SupabaseServerClient | None = None) -> None:
        self.client = client or SupabaseServerClient()

    def _request(self, method: str, **kwargs):
        try:
            return self.client.request(method, "experience_feedback", **kwargs)
        except SupabaseServerError as error:
            raise FeedbackStorageUnavailable("Não foi possível acessar as avaliações.") from error

    def has_feedback(self, participant_id: str) -> bool:
        status, rows = self._request(
            "GET",
            filters={"select": "id", "participant_id": f"eq.{participant_id}", "limit": "1"},
        )
        if status < 200 or status >= 300:
            raise FeedbackStorageUnavailable("Não foi possível verificar sua avaliação.")
        return bool(rows)

    def save_feedback(self, participant_id: str, feedback: dict[str, Any]) -> None:
        status, _ = self._request(
            "POST",
            filters={"on_conflict": "participant_id"},
            payload={"participant_id": participant_id, **feedback},
            prefer="resolution=ignore-duplicates,return=minimal",
        )
        if status < 200 or status >= 300:
            raise FeedbackStorageUnavailable("Não foi possível salvar sua avaliação.")
