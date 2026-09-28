"""Generate a one-time SQL seed document for Supabase SQL Editor."""
import json
from pathlib import Path

from import_catalogs import build_import_payloads

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "supabase-seed-sql.md"


def sql_string(value: object) -> str:
    text = str(value)
    return "'" + text.replace("'", "''") + "'"


def sql_value(value: object, jsonb: bool = False) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return sql_string(json.dumps(value, ensure_ascii=False)) + "::jsonb"
    if isinstance(value, (int, float)):
        return str(value)
    return sql_string(value)


def render_upsert(table: str, columns: list[str], rows: list[dict[str, object]], conflict: str = "id") -> str:
    lines = [f"insert into public.{table} ({', '.join(columns)}) values"]
    values = []
    for row in rows:
        values.append("  (" + ", ".join(sql_value(row.get(column)) for column in columns) + ")")
    lines.append(",\n".join(values) + f"\non conflict ({conflict}) do update set")
    updates = [f"  {column} = excluded.{column}" for column in columns if column != conflict]
    lines.append(",\n".join(updates) + ";\n")
    return "\n".join(lines)


def build_document() -> str:
    payloads = build_import_payloads()
    sections = [
        "# Seed inicial do EcoWatt no Supabase",
        "",
        "Execute a migration estrutural antes deste script. Depois, cole apenas o bloco SQL abaixo no SQL Editor do Supabase.",
        "",
        "Este seed e idempotente: pode ser executado novamente sem duplicar registros. Ele carrega os dados oficiais dos quatro JSONs, todos os itens dos presets e um quiz inicial desabilitado. Dados pessoais nao sao criados com UUID ficticio.",
        "",
        "```sql",
        "begin;",
        "",
    ]
    sections.append(render_upsert("official_appliances", ["id", "name", "normalized_name", "category", "power_watts", "default_hours_per_day", "default_days_per_month", "description", "status", "source"], payloads["official_appliances"]))
    sections.append(render_upsert("official_pc_components", ["id", "name", "normalized_name", "category", "tdp_watts", "idle_watts", "typical_load_watts", "gaming_load_watts", "description", "status", "source"], payloads["official_pc_components"]))
    sections.append(render_upsert("official_facts", ["id", "title", "normalized_title", "body", "status", "source"], payloads["official_facts"]))
    sections.append(render_upsert("official_presets", ["id", "name", "normalized_name", "description", "status", "source"], payloads["official_presets"]))
    sections.append(render_upsert("official_preset_items", ["id", "preset_id", "name", "category", "power_watts", "hours_per_day", "days_per_month", "snapshot"], payloads["official_preset_items"]))
    sections.append(render_upsert("event_quizzes", ["id", "event_key", "title", "enabled", "reward_enabled"], payloads["event_quizzes"]))
    sections.append(render_upsert("quiz_questions", ["id", "quiz_id", "prompt", "explanation", "options", "correct_option", "status"], payloads["quiz_questions"]))
    sections.extend([
        "commit;",
        "```",
        "",
        "## Verificacao",
        "",
        "```sql",
        "select 'official_appliances' as table_name, count(*) as rows from public.official_appliances",
        "union all select 'official_pc_components', count(*) from public.official_pc_components",
        "union all select 'official_facts', count(*) from public.official_facts",
        "union all select 'official_presets', count(*) from public.official_presets",
        "union all select 'official_preset_items', count(*) from public.official_preset_items",
        "union all select 'event_quizzes', count(*) from public.event_quizzes",
        "union all select 'quiz_questions', count(*) from public.quiz_questions",
        "order by table_name;",
        "```",
        "",
    ])
    return "\n".join(sections)


if __name__ == "__main__":
    OUTPUT.write_text(build_document(), encoding="utf-8")
    print(OUTPUT)
