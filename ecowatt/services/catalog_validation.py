"""Validation and deduplication helpers for catalog content."""
import re
import unicodedata
from collections.abc import Iterable, Mapping
from typing import Any, Optional

MAX_NAME_LENGTH = 120
MAX_CATEGORY_LENGTH = 80
MAX_DESCRIPTION_LENGTH = 500
MAX_TEXT_LENGTH = 1000
_UNSAFE_TEXT = re.compile(r"[<>]|(?:javascript|script)\s*:", re.IGNORECASE)


def normalize_name(value: str) -> str:
    """Normalize names for human-friendly duplicate detection."""
    if not isinstance(value, str):
        raise ValueError("O nome deve ser um texto.")
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    normalized = re.sub(r"[^\w\s]", " ", without_accents.casefold())
    return " ".join(normalized.split())


def validate_text(value: Optional[str], field_name: str, max_length: int) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} deve ser um texto.")
    clean_value = value.strip()
    if not clean_value:
        raise ValueError(f"{field_name} nao pode ficar vazio.")
    if len(clean_value) > max_length:
        raise ValueError(f"{field_name} deve ter no maximo {max_length} caracteres.")
    if _UNSAFE_TEXT.search(clean_value):
        raise ValueError(f"{field_name} contem conteudo nao permitido.")
    return clean_value


def validate_number(value: Any, field_name: str, minimum: float = 0.0, maximum: Optional[float] = None) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} deve ser numerico.")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} deve ser numerico.") from exc
    if number < minimum or (maximum is not None and number > maximum):
        limit = f" e {maximum}" if maximum is not None else ""
        raise ValueError(f"{field_name} deve estar entre {minimum}{limit}.")
    return number


def validate_appliance_fields(
    name: str,
    category: str,
    power_watts: Any,
    hours_per_day: Any,
    days_per_month: Any,
    description: Optional[str] = None,
) -> None:
    validate_text(name, "Nome", MAX_NAME_LENGTH)
    validate_text(category, "Categoria", MAX_CATEGORY_LENGTH)
    validate_number(power_watts, "Potencia", maximum=100000)
    validate_number(hours_per_day, "Horas por dia", maximum=24)
    validate_number(days_per_month, "Dias por mes", maximum=31)
    if description:
        validate_text(description, "Descricao", MAX_DESCRIPTION_LENGTH)


def validate_component_fields(
    name: str,
    category: str,
    tdp_watts: Any,
    idle_watts: Any,
    typical_load_watts: Any,
    gaming_load_watts: Any,
    description: Optional[str] = None,
) -> None:
    validate_text(name, "Nome", MAX_NAME_LENGTH)
    validate_text(category, "Categoria", MAX_CATEGORY_LENGTH)
    for field_name, value in (
        ("TDP", tdp_watts),
        ("Potencia ociosa", idle_watts),
        ("Potencia tipica", typical_load_watts),
        ("Potencia em jogos", gaming_load_watts),
    ):
        validate_number(value, field_name, maximum=100000)
    if description:
        validate_text(description, "Descricao", MAX_DESCRIPTION_LENGTH)


def validate_submission_payload(kind: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    if kind not in {"appliance", "pc_component", "fact", "preset"}:
        raise ValueError("Tipo de submissao desconhecido.")
    if not isinstance(payload, Mapping):
        raise ValueError("O conteudo da submissao deve ser um objeto.")
    result = dict(payload)
    for key, value in result.items():
        if isinstance(value, str):
            validate_text(value, key, MAX_TEXT_LENGTH)
    if kind == "appliance":
        validate_appliance_fields(**result)
    elif kind == "pc_component":
        validate_component_fields(**result)
    return result


def duplicate_key(item: Mapping[str, Any], kind: str, owner_user_id: Optional[str] = None) -> tuple[Any, ...]:
    normalized = normalize_name(str(item.get("name", item.get("title", ""))))
    if kind == "appliance":
        fields = (item.get("category", ""), item.get("power_watts"), item.get("hours_per_day"), item.get("days_per_month", 30))
    elif kind == "pc_component":
        fields = (item.get("category", ""), item.get("tdp_watts"), item.get("idle_watts"), item.get("typical_load_watts"), item.get("gaming_load_watts"))
    else:
        fields = ()
    return (owner_user_id, normalized, *fields)


def find_duplicate(items: Iterable[Mapping[str, Any]], candidate: Mapping[str, Any], kind: str, owner_user_id: Optional[str] = None) -> Optional[Mapping[str, Any]]:
    candidate_key = duplicate_key(candidate, kind, owner_user_id)
    return next((item for item in items if duplicate_key(item, kind, owner_user_id) == candidate_key), None)
