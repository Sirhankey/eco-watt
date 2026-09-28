"""Idempotently import the four local JSON catalogs into Supabase."""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "ecowatt" / "data"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ecowatt.services.catalog_validation import normalize_name
SEED_QUIZ_ID = "11111111-1111-4111-8111-111111111111"
SEED_QUESTION_IDS = (
    "22222222-2222-4222-8222-222222222221",
    "22222222-2222-4222-8222-222222222222",
    "22222222-2222-4222-8222-222222222223",
)


def _read_json(filename: str) -> Any:
    with (DATA / filename).open("r", encoding="utf-8") as source:
        return json.load(source)


def build_import_payloads() -> dict[str, list[dict[str, Any]]]:
    appliances = _read_json("appliances.json")
    components_by_category = _read_json("pc_components.json")
    facts = _read_json("facts.json")
    presets = _read_json("presets.json")

    official_appliances = [
        {
            **item,
            "normalized_name": normalize_name(item["name"]),
            "status": "published",
            "source": "migration",
        }
        for item in appliances
    ]
    official_components = [
        {
            **item,
            "normalized_name": normalize_name(item["name"]),
            "status": "published",
            "source": "migration",
        }
        for category, items in components_by_category.items()
        for item in items
    ]
    official_facts = [
        {
            "id": f"fact_{index}",
            "title": item["title"],
            "normalized_title": normalize_name(item["title"]),
            "body": item["fact"],
            "status": "published",
            "source": "migration",
        }
        for index, item in enumerate(facts, start=1)
    ]
    official_presets = [
        {
            "id": preset["id"],
            "name": preset["name"],
            "normalized_name": normalize_name(preset["name"]),
            "description": preset.get("description"),
            "status": "published",
            "source": "migration",
        }
        for preset in presets
    ]
    official_preset_items = [
        {
            "id": item["id"],
            "preset_id": preset["id"],
            "name": item["name"],
            "category": item.get("category", "Geral"),
            "power_watts": item["power_watts"],
            "hours_per_day": item["hours_per_day"],
            "days_per_month": item.get("days_per_month", 30),
            "snapshot": item,
        }
        for preset in presets
        for item in preset.get("appliances", [])
    ]
    event_quizzes = [{
        "id": SEED_QUIZ_ID,
        "event_key": "ecowatt-quiz-basics-2026",
        "title": "Desafio EcoWatt: fundamentos de energia",
        "enabled": False,
        "reward_enabled": False,
    }]
    quiz_questions = [
        {
            "id": question_id,
            "quiz_id": SEED_QUIZ_ID,
            "prompt": prompt,
            "explanation": explanation,
            "options": options,
            "correct_option": correct_option,
            "status": "published",
        }
        for question_id, prompt, explanation, options, correct_option in [
            (SEED_QUESTION_IDS[0], "O que o kWh mede?", "kWh combina potencia e tempo para representar energia consumida.", ["Energia consumida", "Potencia instantanea", "Tensao"], 0),
            (SEED_QUESTION_IDS[1], "Qual unidade mede potencia?", "Watt mede a potencia instantanea de um aparelho.", ["Watt (W)", "Quilowatt-hora (kWh)", "Litro"], 0),
            (SEED_QUESTION_IDS[2], "O que ajuda a reduzir consumo em stand-by?", "Retirar aparelhos da tomada evita consumo quando nao estao em uso.", ["Desligar da tomada", "Aumentar o brilho", "Deixar a luz acesa"], 0),
        ]
    ]
    return {
        "official_appliances": official_appliances,
        "official_pc_components": official_components,
        "official_facts": official_facts,
        "official_presets": official_presets,
        "official_preset_items": official_preset_items,
        "event_quizzes": event_quizzes,
        "quiz_questions": quiz_questions,
    }


def _chunks(items: list[dict[str, Any]], size: int = 100) -> Iterable[list[dict[str, Any]]]:
    for start in range(0, len(items), size):
        yield items[start:start + size]


def import_catalogs(base_url: str, service_role_key: str, dry_run: bool = False) -> int:
    """Upsert catalogs and initial event content, preserving every JSON payload."""
    payloads = build_import_payloads()
    if dry_run:
        return sum(len(records) for records in payloads.values())

    total = 0
    for table, records in payloads.items():
        for batch in _chunks(records):
            body = json.dumps(batch, ensure_ascii=True).encode("utf-8")
            request = urllib.request.Request(
                f"{base_url.rstrip('/')}/rest/v1/{table}",
                data=body,
                method="POST",
                headers={
                    "apikey": service_role_key,
                    "Authorization": f"Bearer {service_role_key}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates,return=minimal",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    if not 200 <= response.status < 300:
                        raise RuntimeError(f"Supabase rejected {table}: HTTP {response.status}")
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                raise RuntimeError(f"Falha ao importar {table}: {exc}") from exc
            total += len(batch)
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    base_url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not args.dry_run and (not base_url or not key):
        parser.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required unless --dry-run is used")
    print(import_catalogs(base_url, key, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
