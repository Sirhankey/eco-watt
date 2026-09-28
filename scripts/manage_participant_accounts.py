"""Reset participant passwords and clean up accounts after the event."""
import argparse
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ecowatt.services.participant_auth import hash_password, normalize_username, validate_password
from ecowatt.services.supabase_server import SupabaseServerClient, SupabaseServerError


def reset_participant_password(client: SupabaseServerClient, username: str, temporary_password: str) -> bool:
    normalized = normalize_username(username)
    validate_password(temporary_password)
    status, participants = client.request(
        "GET",
        "participants",
        filters={"select": "id", "username_normalized": f"eq.{normalized}", "limit": "1"},
    )
    if status < 200 or status >= 300:
        raise SupabaseServerError("Não foi possível consultar a conta no Supabase.")
    if not participants:
        return False

    participant_id = str(participants[0]["id"])
    status, _ = client.request(
        "PATCH",
        "participants",
        filters={"id": f"eq.{participant_id}"},
        payload={"password_hash": hash_password(temporary_password), "must_change_password": True},
        prefer="return=minimal",
    )
    if status < 200 or status >= 300:
        raise SupabaseServerError("Não foi possível redefinir a senha.")

    status, _ = client.request(
        "PATCH",
        "participant_sessions",
        filters={"participant_id": f"eq.{participant_id}", "revoked_at": "is.null"},
        payload={"revoked_at": datetime.now(timezone.utc).isoformat()},
        prefer="return=minimal",
    )
    if status < 200 or status >= 300:
        raise SupabaseServerError("Senha redefinida, mas não foi possível revogar sessões anteriores.")
    return True


def _count_rows(client: SupabaseServerClient, table: str, filters: dict[str, str] | None = None) -> int:
    query = {"select": "id", **(filters or {})}
    status, rows = client.request("GET", table, filters=query)
    if status < 200 or status >= 300:
        raise SupabaseServerError(f"Não foi possível conferir os registros de {table}.")
    return len(rows or [])


def participant_cleanup_counts(client: SupabaseServerClient) -> dict[str, int]:
    owned = {"participant_id": "not.is.null"}
    return {
        "participants": _count_rows(client, "participants"),
        "sessions": _count_rows(client, "participant_sessions", owned),
        "personal_appliances": _count_rows(client, "personal_appliances", owned),
        "personal_presets": _count_rows(client, "personal_presets", owned),
        "catalog_submissions": _count_rows(client, "catalog_submissions", owned),
        "quiz_attempts_retained": _count_rows(client, "quiz_attempts", owned),
    }


def cleanup_participants(
    client: SupabaseServerClient,
    *,
    execute: bool = False,
    purge_results: bool = False,
) -> dict[str, int]:
    counts = participant_cleanup_counts(client)
    if not execute:
        return counts

    status, _ = client.request(
        "DELETE", "participants", filters={"id": "not.is.null"}, prefer="return=minimal"
    )
    if status < 200 or status >= 300:
        raise SupabaseServerError("Não foi possível remover contas e dados pessoais.")

    if purge_results:
        status, _ = client.request(
            "DELETE", "quiz_attempts", filters={"participant_id": "not.is.null"}, prefer="return=minimal"
        )
        if status < 200 or status >= 300:
            raise SupabaseServerError("Contas removidas, mas não foi possível remover resultados do quiz.")
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    reset_parser = commands.add_parser("reset-password", help="Redefinir senha de uma conta participante")
    reset_parser.add_argument("--username", required=True)
    cleanup_parser = commands.add_parser("cleanup", help="Pré-visualizar ou executar a limpeza pós-evento")
    cleanup_parser.add_argument("--execute", action="store_true", help="Executa a limpeza; sem esta opção apenas mostra contagens")
    cleanup_parser.add_argument("--purge-results", action="store_true", help="Também apaga tentativas e respostas pseudonimizadas")
    args = parser.parse_args()
    client = SupabaseServerClient(timeout=10)

    try:
        if args.command == "reset-password":
            temporary_password = getpass("Nova senha temporária: ")
            confirmation = getpass("Confirme a senha temporária: ")
            if temporary_password != confirmation:
                parser.error("As senhas digitadas não conferem.")
            if reset_participant_password(client, args.username, temporary_password):
                print("Senha redefinida. O participante deverá escolher uma nova senha ao entrar.")
            else:
                print("Nenhuma conta encontrada; nada foi alterado.")
            return

        counts = cleanup_participants(client, execute=args.execute, purge_results=args.purge_results)
        print("Registros de conta/dados pessoais:")
        for key in ("participants", "sessions", "personal_appliances", "personal_presets", "catalog_submissions"):
            print(f"  {key}: {counts[key]}")
        print(f"Tentativas pseudonimizadas: {counts['quiz_attempts_retained']}")
        if args.execute:
            print("Limpeza de contas e dados pessoais concluída.")
            print("Tentativas foram removidas." if args.purge_results else "Tentativas pseudonimizadas foram mantidas.")
        else:
            print("Simulação apenas; use --execute para remover contas e dados pessoais.")
    except (SupabaseServerError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()